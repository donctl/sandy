from menu import *
from actions.phonemenu import *
from actions.sdcardmenu import *
from actions.exit import *
from banner import Banner 
        
class Console:
    def __init__(self):

        phone_action = PhoneMenuAction()
        sdcard_action = SDcardMenuAction()
        exit_action = ExitAction()
        
        self.main_menu = Menu("sandy")
        self.main_menu.add_item(Item("Phone", "1", phone_action))
        self.main_menu.add_item(Item("SD card", "2", sdcard_action))
        self.main_menu.add_item(Item("Exit", "99", exit_action))

    def run(self):
        banner = Banner()
        while 1:        
            self.main_menu.draw()
            self.main_menu.do_action()    
