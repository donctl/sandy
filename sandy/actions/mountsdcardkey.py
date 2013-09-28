from action import Action
from modules.sandmountsdcardfromkey.sandmountsdcardfromkey import SandMountSdcardFromKey 
import sandy.sandyutils
import printer
from sandutils import *

class MountSDcardKeyAction(Action):
    __ACTION = "MOUNTSDCARDFROMKEY"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		
		#config=ConfigParser.ConfigParser()
		#config.read("config.cfg")	
		#adb=ADB(config.get("ADB","path"))

		sandmountsdcardfromkey = SandMountSdcardFromKey(prn, sandy.sandy.Sandy._settings['projectname'])

		params=sandmountsdcardfromkey.getparams()	
		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)

		sandmountsdcardfromkey.do()
		
		return
