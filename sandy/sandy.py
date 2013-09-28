from console import Console

class Sandy:
	_settings = {}
	def __init__(self):
		self.console = Console()

	def start_console(self):
		self.console.run()

