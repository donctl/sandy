from action import Action

class BackAction(Action):
    __ACTION = "BACK"

    def do(self):
	raise Exception("Back")
	return	
