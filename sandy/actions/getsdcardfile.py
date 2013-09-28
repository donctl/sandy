from action import Action
from adb.adb import ADB
from modules.sandgetsdcard.sandgetsdcard import SandGetSDCard
import sandy.sandyutils
import printer
import ConfigParser
from sandutils import *

class GetSDCardFileAction(Action):
    __ACTION = "GETSDCARD"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		config=ConfigParser.ConfigParser()
		config.read("config.cfg")

		adb=ADB(config.get("ADB","path"))
		sandgetsdcard = SandGetSDCard(prn, config, sandy.sandy.Sandy._settings['projectname'])
		params=sandgetsdcard.getparams()
		
		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)


		sandgetsdcard.setparams(params)
		sandgetsdcard.get_sdcard_file()
		return
