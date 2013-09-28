from action import Action
from modules.sandmountsdcardfrompwd.sandmountsdcardfrompwd import SandMountSdcardFromPwd 
import sandy.sandyutils
import printer
from sandutils import *

class MountSDcardPwdAction(Action):
    __ACTION = "MOUNTSDCARDFROMPWD"

    def do(self):
		prn = printer.Printer(printer.Printer.UI_CONSOLE)
		
		sandmountsdcardfrompwd = SandMountSdcardFromPwd(prn, sandy.sandy.Sandy._settings['projectname'])
		
		params = sandmountsdcardfrompwd.getparams()
		sandy.sandyutils.print_params(params)
		sandy.sandyutils.set_params(params)

		sandmountsdcardfrompwd.do()
		
		return
