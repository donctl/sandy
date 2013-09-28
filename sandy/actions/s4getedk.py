from action import Action
from adb.adb import ADB
from modules.sands4getedk.sands4getedk import SandS4GetEDK 
import sandy.sandyutils
import printer
import ConfigParser
from sandutils import *

class S4GetEdkAction(Action):
    __ACTION = "S4GETEDK"

    def do(self):
    	
    	prn=printer.Printer(printer.Printer.UI_CONSOLE)

    	config=ConfigParser.ConfigParser()
    	config.read("config.cfg")
    	adb=ADB(config.get("ADB","path"))


    	sands4getedk = SandS4GetEDK(prn, config, sandy.sandy.Sandy._settings['projectname'])

    	params=sands4getedk.getparams()

    	phone = getphonewithos(adb)
    	params["phonewithos"]["value"] = phone
    	config2params(config, params, phone)

    	sandy.sandyutils.print_params(params)
    	sandy.sandyutils.set_params(params)

    	sands4getedk.setparams(params)

    	su=checkforsu(adb)

    	sands4getedk.getedk()

    	return
