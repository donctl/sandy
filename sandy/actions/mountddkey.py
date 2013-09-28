from action import Action
from modules.sandmountddfromkey.sandmountddfromkey import SandMountDDFromKey 
import sandy.sandyutils
import printer
from sandutils import *

class MountDDKeyAction(Action):
    __ACTION = "MOUNTDDFROMKEY"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		
		
		sandmountddfromkey= SandMountDDFromKey(prn, sandy.sandy.Sandy._settings['projectname'])

		params=sandmountddfromkey.getparams()
		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)
		sandmountddfromkey.setparams(params)
	
		sandmountddfromkey.do()
		
		return
