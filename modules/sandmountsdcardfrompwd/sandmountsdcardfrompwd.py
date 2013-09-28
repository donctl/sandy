import re
import sys
import string
import printer
from collections import namedtuple
from binascii import *
from sandutils import *
import os
import subprocess
from modules.sandmountsdcardfromkey.sandmountsdcardfromkey import *

class SandMountSdcardFromPwd(SandMountSdcardFromKey):


   def __init__(self, printer, project):
      self.printer=printer
      self.project=project
      self.params={
		  "out_dir":{"description":"Where to generate the results and download files on the computer.",
			      "value":"results",
			      "required":True
			      },
		  "source_dir":{"description":"Directory contains the files from an encrypted sdcard.",
			      "value":"%s_sdcard/" % self.project,
			      "required":True
			      },
		  "sdcard_file":{"description":"The file contains the encrypted key for the SD card.",
			      "value":"%s_edk_p_sd" % self.project,
			      "required":True
			      },
		   "mnt_dest":{"description":"Where to mount.",
			      "value":"/mnt/sdcard",
			      "required":True
			      },
		  "password":{"description":"Password for the sdcard key decryption.",
			      "value":"qwertz2",
			      "required":True
			      },
		  }
      self.setparams(self.params)

   def setparams(self, params):
      self.params=params
      self.out_dir = self.params["out_dir"]["value"]
      self.password = self.params["password"]["value"]
      self.sdcard_file = self.params["sdcard_file"]["value"]
      self.mnt_dest = self.params["mnt_dest"]["value"]
      self.source_dir = self.params["source_dir"]["value"]

   def getparams(self):
      return self.params

   def getkeybin(self,file):

      """
      Redifine the function here to decrypt the edk_p_sd file with tha password.
      """

      edk=footer2binkey(file, self.password)
      binkey="\x04"+"\0"*11+"\x20"+"\0"*627+"\x20"+"\0"*3+"\x02"+"\0"*3+edk+"\0"*32+hexlify(edk[0:8])+"\0"*12
      return binkey 

   def mountsdcardfrompwd(self, source_dir, sdcard_file, password, mnt_dest):
      self.password=password
      return self.mountsdcardfromkey(source_dir, sdcard_file, mnt_dest)


   def do(self):
      return self.mountsdcardfrompwd("%s/%s" % (self.out_dir,self.source_dir), "%s/%s" % (self.out_dir, self.sdcard_file), self.password, self.mnt_dest)
  
   #def do(self):
   #   return self.mountddfrompwd("%s/%s" % (self.out_dir, self.image_file), self.password, self.mnt_dest)
    
