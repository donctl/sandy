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

class SandSdcKeyctl:


   def __init__(self, printer, config, project, adb_path="adb"):
      self.printer=printer
      self.config=config
      self.project=project
      self.params={"adbpath":{"description":"Path of the adb command",
			      "value":adb_path,
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
		  }
      self.setparams(self.params)

   def setparams(self, params):
      self.params=params
      self.adb = ADB(self.params["adbpath"]["value"])
      self.phone = self.params["phonewithos"]["value"]
      self.out_dir = self.params["out_dir"]["value"]

   def getparams(self):
      return self.params

   def getsdckeybin(self):
      self.printer.print_debug("Check for su!")
      su=checkforsu(self.adb)
      if (su==""):
	 self.printer.print_err("The su comand was not found, hope adb have immediate root access!")
	 su=""
      #No magic here, the phone should be fully booted for this module
      dest_dir="/data/local/tmp"
      self.printer.print_debug("We will use %s on the phone as a destination directory." % dest_dir)
      self.printer.print_info("Uploading keyctl utility to %s..." % dest_dir)
      push=self.adb.push_local_file("keyctl/keyctl","%s" % dest_dir)
      if(push.find("bytes")==-1):
	 self.printer.print_err("Could not upload the keyctl: %s" % push)
	 return -1
      self.printer.print_ok("Upload - Done")
      
      self.printer.print_info("Searching for the keyid...")
      self.printer.print_debug("Running the following command: %s %s/keyctl show @u" % (su, dest_dir))
      out=self.adb.shell_command(su+"%s/keyctl show @u" % (dest_dir))
      self.printer.print_debug("The keys on the keyring:\n%s" % out)
      keyid=""
      for line in out.splitlines():
	 if(line.find("user:")!=-1):
	    keyid=line.lstrip(" ").split(" ")[0]
      
      if(keyid==""):
	 self.printer.print_err("Something went wrong, could not parse 'keyctl show' output.")
	 return -1
      self.printer.print_ok("The keyid is: %s." % (keyid))
      
      self.printer.print_info("Dumping the key...")
      self.printer.print_debug("Running the following command: %s %s/keyctl pipe %s > %s/sdckey.bin" % (su, dest_dir, keyid, dest_dir))
      out=self.adb.shell_command("\"%s %s/keyctl pipe %s > %s/sdckey.bin\"" % (su, dest_dir, keyid, dest_dir))
      if(out!=None):
	 self.printer.print_err("Something went wrong: %s" % (out))
	 return -1

      self.printer.print_info("Downloading the dumped key file...")
      pull=self.adb.get_remote_file("%s/sdckey.bin" % dest_dir,"%s/%s_sdckey.bin" % (self.out_dir, self.project))
      if(pull.find("bytes")==-1):
	 self.printer.print_err("Could not download dumped key file: %s" % pull)
	 self.printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % dest_dir)
	 out=self.adb.shell_command(su+"rm %s/sdckey.bin" % dest_dir)
	 out=self.adb.shell_command(su+"rm %s/keyctl" % dest_dir)
	 return -1
      self.printer.print_ok("Download - Done")
      #self.printer.print_info(pull.rstrip("\n"))
      
      #Cleanup
      self.printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % dest_dir)
      out=self.adb.shell_command(su+"rm %s/sdckey.bin" % dest_dir)
      out=self.adb.shell_command(su+"rm %s/keyctl" % dest_dir)
 
      return 1
 
   def print_info_adb(self,message, ok=True):
      if(ok):
	 self.printer.printer.print_info("OK! Received the following from adb: %s" %message)
      else:
	 self.printer.print_error("ERROR! Received the following from adb: %s" %message)
