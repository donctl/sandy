from sandy.menu import *
from action import Action
from back import BackAction
from phonesand2john import PhoneSand2JohnAction
from dumpfooter import DumpFooterAction
from phonemountmenu import PhoneMountMenuAction
from getdek import GetDekAction
from s4getedk import S4GetEdkAction
from getpwdhash import GetPwdhashAction
from dumpfooterfromdd import DumpFooterFromddAction

class PhoneMenuAction(Action):
    __ACTION = "PHONE"

    def do(self):
        back_action            = BackAction()
        getdek_action          = GetDekAction()
        s4getedk_action        = S4GetEdkAction()
        phonesand2john_action  = PhoneSand2JohnAction()
        dumpfooter_action      = DumpFooterAction()
        phonemountmenu_action  = PhoneMountMenuAction()
        getpwdhash_action      = GetPwdhashAction()
        dumpfooterfromdd_action= DumpFooterFromddAction()

        self.phone_menu = Menu("sandy:phone")
        self.phone_menu.add_item(Item("vold - GetKey", "1", getdek_action))
        self.phone_menu.add_item(Item("Dump footer", "2", dumpfooter_action))
        self.phone_menu.add_item(Item("Dump footer from dd", "3", dumpfooterfromdd_action))
        self.phone_menu.add_item(Item("Convert to JtR", "4", phonesand2john_action))
        self.phone_menu.add_item(Item("Mount", "5", phonemountmenu_action))
        self.phone_menu.add_item(Item("Dump password hash", "6", getpwdhash_action))
        self.phone_menu.add_item(Item("S4 GetEDK", "7", s4getedk_action))
        self.phone_menu.add_item(Item("Back", "99", back_action))

        while 1:
            self.phone_menu.draw()
            try:
                self.phone_menu.do_action()
            except Exception:
                break

        return
