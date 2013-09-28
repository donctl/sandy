from action import Action
from adb.adb import ADB
from modules.sandsdckeyctl.sandsdckeyctl import SandSdcKeyctl
import sandy.sandyutils
import printer
import ConfigParser
from sandutils import *

class SandSdcKeyCtlAction(Action):
    __ACTION = "SANDSDCKEYCTL"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		config=ConfigParser.ConfigParser()
		config.read("config.cfg")
		adb=ADB(config.get("ADB","path"))
		sandsdckeyctl = SandSdcKeyctl(prn, config, sandy.sandy.Sandy._settings['projectname'])
		
		params=sandsdckeyctl.getparams()

		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)

		phone=getphonewithos(adb)
		params["phonewithos"]["value"]=phone
		config2params(config, params, phone)
		
		sandsdckeyctl.setparams(params)
		su=checkforsu(adb)
		sandsdckeyctl.getsdckeybin()

		return
