from adb.adb import ADB
import re
import sys
import string
import printer
import ConfigParser
from pbkdf2 import PBKDF2
import Crypto.Cipher.AES
import Crypto.Hash.HMAC
import Crypto.Hash.SHA256
from binascii import *
import fcntl
import os

#Constants for the footer file decryption
SALT_LEN = 16
KEY_TO_SALT_PADDING = 32
HASH_COUNT = 4096
KEY_LEN_BYTES = 32
IV_LEN_BYTES = 16

def getphonewithos(adb):
   phone=adb.shell_command("getprop ro.product.model").rstrip()
   os=adb.shell_command("getprop ro.build.version.release").rstrip()
   phonewithos="%s %s" % (phone, os)
   return phonewithos

def checkcryptostate(adb):
   state=adb.shell_command("getprop ro.crypto.state").rstrip()
   return state

def checkforsu(adb):
   su="su -c "
   out=adb.shell_command("su -h")
   if (out.find("su: not found")!=-1):
      su=""
   return su

def config2params(config,params,section):
  items = config.items(section)
 
  for (key,value) in items:
    if (key in params):
    	params[key]["value"] = value
  return


def decrypt_key(encrypted_key, salt, password):
      
   #PBKDF2 with SHA256. The first difference from the normal android.
   pbkdf_f = PBKDF2(password, salt,
                     iterations=HASH_COUNT,
                     macmodule=Crypto.Hash.HMAC,
                     digestmodule=Crypto.Hash.SHA256)
   key = pbkdf_f.read(KEY_LEN_BYTES)
   iv = pbkdf_f.read(IV_LEN_BYTES)
   iv="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
   fixed_hex_1="\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
   fixed_hex_2="\x01\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
   cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
   first_half = bytearray(cipher.encrypt(fixed_hex_1))
   cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
   second_half = bytearray(cipher.encrypt(fixed_hex_2))
   byte_encrypted_key=bytearray(encrypted_key)
   decrypted_key=bytearray(32)
   for i in range(16):
      decrypted_key[i]=first_half[i] ^ byte_encrypted_key[i]
   for i in range(16):
      decrypted_key[i+16]=second_half[i] ^ byte_encrypted_key[i+16]

   return decrypted_key,key

def create_padding(encrypted_key, master_key):
   h = Crypto.Hash.HMAC.new(master_key, digestmod=Crypto.Hash.SHA256)
   h.update(encrypted_key)
   return h.digest()




def footer2binkey(footerfile, password):
   binkey=""
   mode="phone"
   try:
      f = open(footerfile,"rb")
      try:
	 f.seek(0x24)
	 check=f.read(3)
	 if(check=="aes"):
	    mode="phone"
	 else:
	    mode="sdcard"
	 if(mode=="sdcard"):
	    offset=0x20
	 else:
	    offset=0x84
	 f.seek(offset)
	 keypaddingsalt=f.read(80)
      finally:
	 f.close()
   except IOError as e:
      prn=printer.Printer(printer.Printer.UI_CONSOLE)
      prn.print_err("I/O error({0}): {1}: {2}".format(e.errno, e.strerror, file))
      return -1
      
   binkey,mkey = decrypt_key(keypaddingsalt[:32], keypaddingsalt[64:], password)
   padding=create_padding(keypaddingsalt[:32], mkey)
  
   return binkey


def setnonblock(out):
   fd = out.fileno()
   fl = fcntl.fcntl(fd, fcntl.F_GETFL)
   fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

def check_tmp(printer,adb,su):
   #printer.print_info("Check the /tmp directory")
   dest_dir="/tmp"
   out = adb.shell_command(su+"ls /tmp")
   if(out):
      if (out.find("No such file or directory")!=-1):
         #printer.print_err("The /tmp directory was not found! Try the /data/local/tmp directory!")

         out=adb.shell_command(su+"ls /data/local/tmp")
	      #if the directory empty, we will receive NoneType
         if (out):
            if (out.find("No such file or directory")!=-1):
	           printer.print_err("The /data/local/tmp directory was not found!")
	           printer.print_err("Did not found suitable destination directory! Please start the phone in a proper recovery mode.")
	           return -1
         dest_dir="/data/local/tmp"

   printer.print_debug("Use %s on the phone as a detination directory!" % dest_dir)
   return dest_dir

def get_file(printer, adb, su, source, destination):  
   tmp_dir = check_tmp(printer,adb,su)
   file_name = os.path.basename(source)
   tmp_dest = "%s/%s" % (tmp_dir,file_name)

   ''' Copy the file to the TEMP folder '''
   out=adb.shell_command(su+"'cat %s >%s'" % (source,tmp_dest))

   if( (out!=None) and (out.find("Read-only")!=-1) ):
      printer.print_err("The /tmp directory is readonly! Let's use /data/local/tmp")
      tmp_dir="/data/local/tmp"
      out=adb.shell_command(su+"'cat %s >%s'" % (source,tmp_dest))
      if(out!=None): 
         printer.print_err("Unknown error: %s!" % (out))
         return -1
   
   
   ''' Change the permissions to be able to read the file'''
   out=adb.shell_command(su+"chmod 666 %s" % (tmp_dest))
   if(out!=None):
      printer.print_err("Unknown error: %s!" % (out))
      printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % tmp_dir)
      out=adb.shell_command(su+"rm %s" % tmp_dest)
      if (out==None):
         printer.print_ok("Clean up - Done")
      return -1

   ''' Download the file from the TEMP folder'''
   pull=adb.get_remote_file("%s" % tmp_dest,"%s" % destination)
   if(pull.find("bytes")==-1):
      printer.print_err("Could not download the file: %s" % pull)
      printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % tmp_dir)
      out=adb.shell_command(su+"rm %s" % tmp_dest)
      if (out==None):
         printer.print_ok("Clean up - Done")
      return -1   
      
   '''self.printer.print_info(pull.rstrip("\n"))'''

   ''' cleanup'''
   printer.print_info("Cleaning up! Please check the %s folder. Unsuccessull cleanup weakens the security of the phone!!!!" % tmp_dir)
   out=adb.shell_command(su+"rm %s" % tmp_dest)
   if (out==None):
         printer.print_ok("Clean up - Done")
   return pull      
