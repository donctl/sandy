from action import Action
from adb.adb import ADB
from modules.sandgetfooter.sandgetfooter import SandGetFooter
import sandy.sandyutils
import printer
import ConfigParser
from sandutils import *

class DumpFooterAction(Action):
    __ACTION = "DUMPFOOTER"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		config=ConfigParser.ConfigParser()
		config.read("config.cfg")
		#prn.print_info(config.sections())

		adb = ADB(config.get("ADB","path"))

		sandgetfooter = SandGetFooter(prn, config, sandy.sandy.Sandy._settings['projectname'])
		
		params = sandgetfooter.getparams()

		phone = getphonewithos(adb)
		#phone="GT-I9300 4.1.2"
		params["phonewithos"]["value"] = phone
		config2params(config, params, phone)
		
		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)

		sandgetfooter.setparams(params)
		

		su=checkforsu(adb)
		sandgetfooter.getfooter()
		
