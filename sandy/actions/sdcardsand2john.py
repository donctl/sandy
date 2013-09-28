from action import Action
from adb.adb import ADB
from modules.sand2john.sand2john import Sand2John
import sandy.sandyutils
import printer
import ConfigParser
from sandutils import *

class SdcardSand2JohnAction(Action):
    __ACTION = "SDCARDSAND2JOHN"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		sand2john = Sand2John(prn, sandy.sandy.Sandy._settings['projectname'], mode="sdcard")
		
		params=sand2john.getparams()
		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)
		sand2john.setparams(params)
		
		sand2john.convert2john()	
		return
