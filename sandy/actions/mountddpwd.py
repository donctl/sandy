from action import Action
from modules.sandmountddfrompwd.sandmountddfrompwd import SandMountDDFromPwd 
import sandy.sandyutils
import printer
from sandutils import *

class MountDDPwdAction(Action):
    __ACTION = "MOUNTDDFROMPWD"

    def do(self):
		prn=printer.Printer(printer.Printer.UI_CONSOLE)
		
		sandmountddfrompwd=SandMountDDFromPwd(prn, sandy.sandy.Sandy._settings['projectname'])

		params=sandmountddfrompwd.getparams()
		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)
		sandmountddfrompwd.setparams(params)
		
		sandmountddfrompwd.do()
		
		return
