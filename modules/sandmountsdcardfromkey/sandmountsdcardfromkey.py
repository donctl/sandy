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
import time

class SandMountSdcardFromKey:


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
		  "sdckey":{"description":"The file contains the decrypted key for the SD card.",
			      "value":"%s_sdckey.bin" % self.project,
			      "required":True
			      },
		   "mnt_dest":{"description":"Where to mount.",
			      "value":"/mnt/sdcard",
			      "required":True
			      },
		  }
      self.setparams(self.params)


   def setparams(self, params):
      self.params=params
      self.out_dir = self.params["out_dir"]["value"]
      self.source_dir = self.params["source_dir"]["value"]
      self.sdckey = self.params["sdckey"]["value"]
      self.mnt_dest = self.params["mnt_dest"]["value"]

   def getparams(self):
      return self.params
   
   def getkeybin(self, file):
      try:
	 f=open(file,"rb")
	 try:
	    binkey=f.read()
	 finally:
	    f.close()
      except IOError as e:
	 self.printer.print_err("I/O error({0}): {1} {2}/{3}".format(e.errno, e.strerror, self.out_dir, self.image_file))
	 return ""
      return binkey
      

   def mountsdcardfromkey(self, source_dir, sdckey, mnt_dest):
      
      """
      Runs the following two commands to mount a directory that conatins files from an encrypted SD card
      keyctl padd user 6f373de316226c3d  @u < s4_sdckey.bin
      mount -r -i -t ecryptfs sdcard/ /mnt/sdcard/ -o ecryptfs_sig=5c6f31e3a9376cff,ecryptfs_cipher=aes,\
      ecryptfs_key_bytes=32,ecryptfs_unlink_sigs,ecryptfs_enable_filename_crypto=n,no_sig_cache,ecryptfs_passthrough
      """
      
      binkey=self.getkeybin(sdckey)
     
      #Key signature from the dumped key file 
      keyid=binkey[712:].rstrip("\0")
      command=["keyctl", "padd", "user", "%s" % keyid, "@u"]
      self.printer.print_debug("Add the key to your keyring with the following command")
      self.printer.print_debug(" ".join(command))
      try:
	 keyctl=subprocess.Popen(command,stderr=subprocess.STDOUT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	 out=keyctl.communicate(binkey)
      except subprocess.CalledProcessError as error:
	 self.printer.print_err("keyctl failed: %d" % error.returncode)
	 self.printer.print_err(error.output)
	 return -1
      except Exception as error:
	 self.printer.print_err("keyctl failed: %s" % error.strerror)
	 self.printer.print_err("keyctl is installed?")
	 return -1
      
      if(out[1]!=None):
	 self.printer.print_err("keyctl failed: %s" % out[1])
	 self.printer.print_err("keyctl is installed?")
	 return -1
      
      self.printer.print_ok("Key was added to the keyring. The keyid is %s" % out[0].rstrip("\n"))

      command=['mount', '-r', '-i', '-t', 'ecryptfs', source_dir,  mnt_dest, '-o',
	 'ecryptfs_sig=%s,ecryptfs_cipher=aes,ecryptfs_key_bytes=32,ecryptfs_unlink_sigs,ecryptfs_enable_filename_crypto=n,no_sig_cache,ecryptfs_passthrough' % keyid]
      self.printer.print_debug("Mount the %s directory with the following command:" % (source_dir))
      self.printer.print_debug(" ".join(command))
      try:
	 mount=subprocess.check_output(command,stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as error:
	 self.printer.print_err("mount failed: %d" % error.returncode)
	 self.printer.print_err(error.output)
	 return -1
      except Exception as error:
	 self.printer.print_err("mount failed: %s" % error.strerror)
	 return -1
      
      self.printer.print_ok("Mount - Done")
      self.printer.print_ok("Mount destination: %s" % self.mnt_dest)
      
      return 1

   def do(self):
      return self.mountsdcardfromkey( "%s/%s" % (self.out_dir,self.source_dir), "%s/%s" % (self.out_dir, self.sdckey), self.mnt_dest)

