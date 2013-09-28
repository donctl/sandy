from action import *
import sys
class ExitAction(Action):
    __ACTION = "EXIT"

    def do(self):
        a = raw_input("Are you sure? [y/n] ").upper()
        while not (a in ["Y","N"]):
            a = raw_input("Are you sure? [y/n] ").upper()
        if (a=="Y"):
            sys.exit()
