from sandy.menu import *
from action import Action
from back import BackAction
from mountsdcardkey import MountSDcardKeyAction
from mountsdcardpwd import MountSDcardPwdAction

class SDcardMountMenuAction(Action):
    __ACTION = "SDCARD_MOUNT"

    def do(self):
        back_action      =  BackAction()
        mountsdcardkey_action = MountSDcardKeyAction()
        mountsdcardpwd_action = MountSDcardPwdAction()

        self.sdcard_mount_menu = Menu("sandy:sdcard:mount")
        self.sdcard_mount_menu.add_item(Item("Mount SD card image from key file", "1", mountsdcardkey_action))
        self.sdcard_mount_menu.add_item(Item("Mount SD card image from password", "2", mountsdcardpwd_action))
        self.sdcard_mount_menu.add_item(Item("Back", "99", back_action))
       
	while 1:
	  self.sdcard_mount_menu.draw()
          try:
	    self.sdcard_mount_menu.do_action()
	  except Exception:
	    break

	return
