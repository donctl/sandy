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

class SandGetSDCard:


   def __init__(self, printer, config, project, adb_path="adb"):
      self.printer=printer
      self.config=config
      self.project=project
      self.params={"adbpath":{"description":"Path of the adb command",
			      "value":adb_path,
			      "required":True
			      },
		  "out_dir":{"description":"Where to generate the results and download files on the computer.",
			      "value":"results",
			      "required":True
			      },
		  "sdcard_file":{"description":"The DEK is stored in this file on the phone.",
			      "value":"/data/system/edk_p_sd",
			      "required":True
			      },
		  }
      self.setparams(self.params)

   def setparams(self, params):
      self.params=params
      self.adb = ADB(self.params["adbpath"]["value"])
      self.sdcard_file = os.path.basename(self.params["sdcard_file"]["value"])
      self.out_dir = self.params["out_dir"]["value"]

   def getparams(self):
      return self.params

   def get_sdcard_file(self):
      '''
      Downloads the sdcard_file (typically /data/system/edk_p_sd).
      It copies the file to /tmp or /data/local/tmp. Changes the access right to adb pull and downloads it.
      '''

      self.printer.print_debug("Check for su!")
      su=checkforsu(self.adb)
      if (su==""):
	 self.printer.print_err("The su comand was not found, hope the phone in a recovery with root access!")
	 su=""

  
      self.printer.print_info("Download key file")
      pull = get_file(self.printer,self.adb,su,"%s" %(self.params["sdcard_file"]["value"]),"%s/%s_%s" % (self.out_dir, self.project, self.sdcard_file))
      self.printer.print_ok("Download - Done")
      self.printer.print_info(pull.rstrip("\n"))

      return 1

   
