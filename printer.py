class Printer:
    UI_CLI     = 0
    UI_CONSOLE = 1

    INFOBLUE = '\033[96m'
    OKGREEN  = '\033[92m'
    DEBUG    = '\033[93m'
    FAIL     = '\033[91m'
    ENDC     = '\033[0m'

    
    def __init__(self,uitype=0,textcontrol=None):
        self.set_uitype(uitype)
   
    def set_uitype(self,uitype):
        if uitype == Printer.UI_CLI:
            self.printer = CliPrinter()
        elif uitype == Printer.UI_CONSOLE:
            self.printer = ConsolePrinter()
        else:
            self.printer = CliPrinter()
        
    def print_err(self,text):    
        self.printer.print_err(text)
        
    def print_ok(self,text):
        self.printer.print_ok(text)
        
    def print_info(self,text):
        self.printer.print_info(text)

    def print_debug(self,text):
        self.printer.print_debug(text)

class CliPrinter(Printer):
    def __init__(self):
        return
        
    def print_err(self,text):    
        print(text)
        
    def print_ok(self,text):
        print(text)
        
    def print_info(self,text):
        print (text)    

    def print_debug(self,text):
        print (text)

class ConsolePrinter(Printer):
    def __init__(self):
        return
    
    def print_err(self,text):
        print self.FAIL+    "[ ERROR ]: "+text+self.ENDC
        
    def print_ok(self,text):
        print self.OKGREEN+ "[ OK    ]: "+text+self.ENDC
        
    def print_info(self,text):
        print self.INFOBLUE+"[ INFO  ]: "+text+self.ENDC
        
    def print_debug(self,text):
        print self.DEBUG+   "[ DEBUG ]: "+text+self.ENDC
        
