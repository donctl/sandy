from action import Action
from adb.adb import ADB
from modules.sandgetfooterfromdd.sandgetfooterfromdd import SandGetFooterFromdd
import sandy.sandyutils
import printer
import ConfigParser
from sandutils import *

class DumpFooterFromddAction(Action):
    __ACTION = "DUMPFOOTERFROMDD"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		sandgetfooterfromdd = SandGetFooterFromdd(prn, sandy.sandy.Sandy._settings['projectname'])
		params = sandgetfooterfromdd.getparams()

		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)

		sandgetfooterfromdd.setparams(params)
		

		sandgetfooterfromdd.do()
		
