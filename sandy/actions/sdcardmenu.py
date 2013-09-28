from sandy.menu import *
from action import Action
from back import BackAction
from sdcardsand2john import SdcardSand2JohnAction
from getsdcardfile import GetSDCardFileAction
from sandsdckeyctl import SandSdcKeyCtlAction
from sdcardmountmenu import SDcardMountMenuAction

class SDcardMenuAction(Action):
    __ACTION = "SDCARD"

    def do(self):
        back_action          = BackAction()
        sdcardsand2john_action     = SdcardSand2JohnAction()
        getsdcard_action     = GetSDCardFileAction()
        sandsdckeyctl_action = SandSdcKeyCtlAction()
        sdcardmountmenu_action  = SDcardMountMenuAction()

        self.sdcard_menu = Menu("sandy:sdcard")
        self.sdcard_menu.add_item(Item("Get keyfile", "1", getsdcard_action))
        self.sdcard_menu.add_item(Item("Convert to JtR", "2", sdcardsand2john_action))
        self.sdcard_menu.add_item(Item("Mount", "3", sdcardmountmenu_action))
        self.sdcard_menu.add_item(Item("Keyctl", "4", sandsdckeyctl_action))
        self.sdcard_menu.add_item(Item("Back", "99", back_action))

        while 1:
            self.sdcard_menu.draw()
            try:
                self.sdcard_menu.do_action()
            except Exception:
                break

        return
