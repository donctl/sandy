class Menu:
    MENU_HEADER = "Select from the menu:"

    def __init__(self, name, items=None):
        self.name = name
        self.items = items or []
        self.valid_keycodes = ["e","E"]
	self.prompt='\033[1;94m'+name+"> "+'\033[0m'

    def add_item(self, item):
        self.items.append(item)
        self.valid_keycodes.append(item.keycode)
        if item.parent != self:
            item.parent = self

    def remove_item(self, item):
        self.items.remove(item)
        self.valid_keycodes.remote(item.keycode)
        if item.parent == self:
            item.parent = None

    def draw(self):
	print "\n%s\n"%self.MENU_HEADER
        for item in self.items:
            item.draw()
	print ""
        
    def get_item(self,keycode):
        for item in self.items:
            if (item.keycode == keycode):
                return item
        return None
    
    def do_action(self):
        keycode = raw_input(self.prompt)
        while not (keycode in self.valid_keycodes):
            keycode = raw_input(self.prompt)
        
        if (keycode == "e" or keycode == "E"):
            exit(0)  
        selected_item = self.get_item(keycode)
	
        if (selected_item):
            return selected_item.do()
        return None
   
class Item:
    __KEYCODE_PADDING = 3
    
    def __init__(self, name, keycode, action_object, parent=None):
        self.name = name
        self.action = action_object
        self.parent = parent
        self.keycode = keycode
        if parent:
            parent.add_item(self)
             
    def do(self):
        if (self.action):
            return self.action.do()
        return None
    
    def print_item(self,text):
        print text

    def draw(self):
        n = len(self.keycode)
        s = ""
        for i in range(self.__KEYCODE_PADDING-n):
            s+=" "
        s+=self.keycode
        self.print_item(s+" - " + "[ "+self.name+" ]")
        
