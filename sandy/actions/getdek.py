from action import Action
from adb.adb import ADB
from modules.sandgetdek.sandgetdek import GetKey 
import sandy.sandyutils
import printer
import ConfigParser
from sandutils import *

class GetDekAction(Action):
    __ACTION = "GETDEK"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		
		config=ConfigParser.ConfigParser()
		config.read("config.cfg")
		adb=ADB(config.get("ADB","path"))

		getkey = GetKey(prn, config, sandy.sandy.Sandy._settings['projectname'])
		
		params=getkey.getparams()
		
		phone = getphonewithos(adb)
		#phone="GT-I9300 4.1.2"
		params["phonewithos"]["value"] = phone
		config2params(config, params, phone)

		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)

		getkey.setparams(params)

		if(getkey.get_vold_data_segment()==-1):
   			print "Could not get vold memory."

		prn.print_info("Extract the strings from the memory dump. The password or pin should be there.")
		getkey.getpin()

		return
