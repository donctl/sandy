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

class SandMountDDFromKey:


   def __init__(self, printer, project):
      self.printer=printer
      self.project=project
      self.params={
		  "out_dir":{"description":"Where to generate the results and download files on the computer.",
			      "value":"results",
			      "required":True
			      },
		  "image_file":{"description":"The dd image of the encrypted phone.",
			      "value":"%s_data.dd" % self.project,
			      "required":True
			      },
		  "dekfile":{"description":"Where to generate the results and download files on the computer.",
			      "value":"%s_dek.bin.1" % self.project,
			      "required":True
			      },
		   "mnt_dest":{"description":"Where to mount.",
			      "value":"/mnt/userdata",
			      "required":True
			      },
		  }
      self.setparams(self.params)


   def setparams(self, params):
      self.params=params
      self.out_dir = self.params["out_dir"]["value"]
      self.dekfile = self.params["dekfile"]["value"]
      self.image_file = self.params["image_file"]["value"]
      self.mnt_dest = self.params["mnt_dest"]["value"]

   def getparams(self):
      return self.params

   def mountddfromkey(self, image_file, dekfile, mnt_dest):

      self.printer.print_info("Trying to mount the dd file...")

      command=["cryptsetup", "-h", "plain", "-c",
	     "aes-cbc-essiv:sha256", "--readonly", "-d", dekfile, "create", "userdata",image_file]
      self.printer.print_debug("Set up the dm-crypt with the following command: ")
      self.printer.print_debug(" ".join(command))
      try:
	 a=subprocess.check_output(command,stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as error:
	 self.printer.print_err("cryptsetup failed: %d" % error.returncode)
	 self.printer.print_err(error.output)
	 return -1
      except Exception as error:
	 self.printer.print_err("cryptsetup failed: %s" % error.strerror)
	 self.printer.print_err("cryptsetup is installed?")
	 return -1

      command=["mount", "-r", "/dev/mapper/userdata", "%s" % mnt_dest]
      self.printer.print_debug(" ".join(command))
      
      try:
	 a=subprocess.check_output(command,stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as error:
	 self.printer.print_err("mount failed: %d" % error.returncode)
	 self.printer.print_err(error.output)
	 return -1
      except Exception as error:
	 self.printer.print_err("mount failed: %s" % error.strerror)
	 return -1
      
      self.printer.print_ok("Mount - Done")
      self.printer.print_ok("Mount destination: %s" % mnt_dst)
      return 1

   def do(self):
      return self.mountddfromkey("%s/%s" % (self.out_dir, self.image_file), "%s/%s" % (self.out_dir, self.dekfile), self.mnt_dest)
      
