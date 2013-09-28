from action import Action
from adb.adb import ADB
from modules.sandgetpwdhash.sandgetpwdhash import SandGetPasswordHash
import sandy.sandyutils
import printer
import ConfigParser
from sandutils import *

class GetPwdhashAction(Action):
    __ACTION = "GETPWDHASH"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		config=ConfigParser.ConfigParser()
		config.read("config.cfg")
		#prn.print_info(config.sections())

		
		adb = ADB(config.get("ADB","path"))
		sandgetpwdhash = SandGetPasswordHash(prn, config, sandy.sandy.Sandy._settings['projectname'])
		
		params = sandgetpwdhash.getparams()


		phone = getphonewithos(adb)
		#phone="GT-I9505 4.2.2"
		params["phonewithos"]["value"] = phone
		config2params(config, params, phone)
		
		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)

		sandgetpwdhash.setparams(params)
		

		su=checkforsu(adb)
		sandgetpwdhash.dump_hash()	
