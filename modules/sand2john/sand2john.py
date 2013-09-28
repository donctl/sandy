import re
import sys
import string
import printer
from collections import namedtuple
from binascii import *
from sandutils import *

class Sand2John:


   def __init__(self, printer, project, mode="phone"):
      self.printer=printer
      self.project=project
      self.mode=mode
      if(self.mode=="sdcard"):
	 key_file="edk_p_sd"
      else:
	 key_file="footer"
      self.params={
		  "out_dir":{"description":"Where to generate the results on the computer.",
			      "value":"results",
			      "required":True
			      },
		  "key_file":{"description":"The footer file or the SD card file that kontains the encrypted key.",
			      "value":"%s_%s" % (self.project, key_file),
			      "required":True
			      },
		  }
      self.setparams(self.params)

   def setparams(self, params):
      self.params=params
      self.out_dir = self.params["out_dir"]["value"]
      self.key_file = self.params["key_file"]["value"]

   def getparams(self):
      return self.params

   def convert2john(self):
      toconvert="%s/%s" % (self.out_dir, self.key_file)
      if(self.fileconvert2john(toconvert)==-1):
	 return -1
      return 1

   def fileconvert2john(self, file):
      mode="phone"
      try:
	 f = open(file,"rb")
	 f.seek(0x24)
	 check=f.read(3)
	 if(check=="aes"):
	    mode="phone"
	 else:
	    mode="sdcard"
      except IOError as e:
	 self.printer.print_err("I/O error({0}): {1}: {2}".format(e.errno, e.strerror, file))
	 return -1
      self.printer.print_info("Converting %s encryption file to sandcrypt jtr format." % mode)
      if(mode=="sdcard"):
	 offset=0x20
      else:
	 offset=0x84
      
      f.seek(offset)
      binary=f.read(80)
      f.close()
      john=hexlify(binary)
      self.printer.print_ok("Convert - Done")
      self.printer.print_info("This will be written to file %s/%s_sanddek.jtr, for jtr:" % (self.out_dir, self.project))
      self.printer.print_info("%s%s:%s" % (self.project, mode, john))
      self.printer.print_ok("Write - Done")
      try:
	 f= open("%s/%s_sanddek.jtr" % (self.out_dir, self.project), "a")
	 f.write("%s%s:%s\n" % (self.project, mode, john))
	 f.close()
      except IOError as e:
	 self.printer.print_err("I/O error({0}): {1}: {2}/{3}_sanddek.jtr".format(e.errno, e.strerror, self.out_dir, self.project))
	 return -1
      return 1

