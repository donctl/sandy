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

class SandGetFooterFromdd:


   def __init__(self, printer, project):
      self.printer=printer
      self.project=project
      self.params={
		  "out_dir":{"description":"Where to generate the results and download files on the computer.",
			      "value":"results",
			      "required":True
			      },
		  "image_file":{"destion":"The dd image of the encrypted phone.",
			      "value":"%s_data.dd" % self.project,
			      "required":True
			      },
		  }
      self.setparams(self.params)

   def setparams(self, params):
      self.params=params
      self.image_file = self.params["image_file"]["value"]
      self.out_dir = self.params["out_dir"]["value"]

   def getparams(self):
      return self.params

   def get_footer_from_dd(self,image_file):

      '''
      Extract the last 16k from the image file. The DEK should be there.
      '''
      buff=""
      self.printer.print_info("Opening the dd image file: %s..." % image_file)
      try:
            f=open(image_file,"rb")
            try:
                  f.seek(-0x4000, os.SEEK_END)
                  buff=f.read(0x4000)
            finally:
                  f.close()
      except IOError as e:
            self.printer.print_err("I/O error({0}): {1} {2}".format(e.errno, e.strerror, image_file))
            return -1
     
      self.printer.print_ok("Open - Done")
 
      self.printer.print_info("Writing the last 16k to the following file: %s/%s_footer.." % (self.out_dir, self.project))
      try:
            f=open("%s/%s_footer" % (self.out_dir, self.project),"wb")
            try:
                  f.write(buff)
            finally:
                  f.close()
      except IOError as e:
            self.printer.print_err("I/O error({0}): {1} {2}/{3}_footer".format(e.errno, e.strerror, self.out_dir, self.project))
            return -1
            
      self.printer.print_ok("Write - Done")
      return 1

   def do(self):
      return self.get_footer_from_dd("%s/%s" % (self.out_dir, self.image_file))

   
