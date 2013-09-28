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

class SandGetFooter:


   def __init__(self, printer, config, project, adb_path="adb"):
      self.printer=printer
      self.config=config
      self.project=project
      self.params={"adbpath":{"description":"Path of the adb command",
			      "value":adb_path,
			      "required":True
			      },
		  "footer":{"description":"Is the key is stored in footer?",
			      "value":"True",
			      "required":True
			      },
		  "phonewithos":{"description":"The samsung hardware and the android version",
			      "value":"GT-I9300 4.1.2",
			      "required":True
			      },
		  "out_dir":{"description":"Where to generate the results and download files on the computer.",
			      "value":"results",
			      "required":True
			      },
		  "footer_file":{"description":"The DEK is stored in this file on the phone.",
			      "value":"/efs/metadata",
			      "required":True
			      },
		  }
      self.setparams(self.params)

   def setparams(self, params):
      self.params=params
      self.adb = ADB(self.params["adbpath"]["value"])
      self.phone = self.params["phonewithos"]["value"]
      self.out_dir = self.params["out_dir"]["value"]
      self.footer_file = self.params["footer_file"]["value"]

   def getparams(self):
      return self.params

   
   def get_footer_from_phone(self):
      
      '''
      Uploads the seek_and_read to /tmp or /data/local/tmp and runs it. Then it downloads the result footer file.
      It dumps the last 16K of the data partition, configure in the config.cfg file. Please check the given
      directories on the phone to make sure the cleanup was ok.
      '''
      
      partition=self.config.get(self.phone, "data")
      self.printer.print_debug(partition)
      self.printer.print_debug("Check for su!")
      su=checkforsu(self.adb)
      if (su==""):
	 self.printer.print_err("The su comand was not found, hope the phone in a recovery with root access!")
	 su=""
      
      #dd was too slow on the phone (5min on s3), thus we implemented a seek and read program.
   
      dest_dir=check_tmp(self.printer,self.adb,su)
      self.printer.print_info("Uploading the footer reader to %s..." % (dest_dir))
      push=self.adb.push_local_file("seek_and_read/seek_and_read","%s" % dest_dir)
      if(push.find("bytes")==-1):
	 self.printer.print_err("Could not upload the file reader: %s" % push)
	 return -1
      self.printer.print_ok("Upload - Done")

      self.printer.print_debug("Running the following command:")
      command=su+"%s/seek_and_read %s %s/footer" % (dest_dir, partition, dest_dir)
      self.printer.print_debug(command)
      out=self.adb.shell_command(command)
      if(out.find("16384")==-1):
	 self.printer.print_err("File reader did not work: %s" % out)
	 self.printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % dest_dir)
	 out=self.adb.shell_command(su+"rm %s/footer" % dest_dir)
	 out=self.adb.shell_command(su+"rm %s/seek_and_read" % dest_dir)
	 return -1
      
      self.printer.print_info("Downloading the footer file...")
      pull=self.adb.get_remote_file("%s/footer" % dest_dir,"%s/%s_footer" % (self.out_dir, self.project))
      if(pull.find("bytes")==-1):
	 self.printer.print_err("Could not download footer file: %s" % pull)
	 self.printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % dest_dir)
	 out=self.adb.shell_command(su+"rm %s/footer" % dest_dir)
	 out=self.adb.shell_command(su+"rm %s/seek_and_read" % dest_dir)
	 return -1 	
      self.printer.print_ok("Download - Done") 
      self.printer.print_info(pull.rstrip("\n"))
      
      #Cleanup
      self.printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % dest_dir)
      out=self.adb.shell_command(su+"rm %s/footer" % dest_dir)
      out=self.adb.shell_command(su+"rm %s/seek_and_read" % dest_dir)

      self.printer.print_ok("Download - Done")
      return 1

   def get_footer_file(self):

      '''
      Downloads the footer_file (typical /efs/metadata) that contains the DEK on S2. It copies the file to /tmp
      or /data/local/tmp. Changes the access right to adb pull and downloads it.
      '''

      self.printer.print_debug("Check for su!")
      su=checkforsu(self.adb)
      if (su==""):
	 self.printer.print_err("The su comand was not found, hope the phone in a recovery with root access!")
	 su=""

      self.printer.print_info("Downloading the footer [ %s ] file" % self.params["footer_file"])
      pull = get_file(self.printer, self.adb, su, self.params["footer_file"], "%s/%s_footer"%(self.out_dir, self.project))
      if (pull!=-1):
	 self.printer.print_ok("Download - Done")
      return pull

   def getfooter(self):

      '''
      Decides whether the DEK is stored in file or at the end of data partition. The decision is based on the
      config.cg file.
      '''

      if(self.params["footer"]["value"]=="n"):
	 if(self.get_footer_file()==-1):
	    return -1
      else:
	 if(self.get_footer_from_phone()==-1):
	    return -1
      return 1

   
   def print_info_adb(self,message, ok=True):
      if(ok):
	 self.printer.printer.print_info("OK! Received the following from adb: %s" %message)
      else:
	 self.printer.print_error("ERROR! Received the following from adb: %s" %message)
