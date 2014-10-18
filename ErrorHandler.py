'''
Created on 04.01.2014

@author: bkerler
#Added exception handling
'''

class ADBError(Exception):
    def __init__ (self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)        