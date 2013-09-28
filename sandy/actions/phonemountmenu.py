from sandy.menu import *
from action import Action
from back import BackAction
from mountddkey import MountDDKeyAction
from mountddpwd import MountDDPwdAction

class PhoneMountMenuAction(Action):
    __ACTION = "PHONE_MOUNT"

    def do(self):
        back_action      = BackAction()
        mountddkey_action = MountDDKeyAction()
        mountddpwd_action = MountDDPwdAction()

        self.phone_mount_menu = Menu("sandy:phone:mount")
        self.phone_mount_menu.add_item(Item("Mount DD image from key file", "1", mountddkey_action))
        self.phone_mount_menu.add_item(Item("Mount DD image from password", "2", mountddpwd_action))
        self.phone_mount_menu.add_item(Item("Back", "99", back_action))
       
	while 1:
	  self.phone_mount_menu.draw()
          try:
	    self.phone_mount_menu.do_action()
	  except Exception:
	    break

	return
