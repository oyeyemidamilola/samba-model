# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 22:41:00 2019

@author: USER
"""

class InvalidExtensionError(Exception):
    
    
    def __init__(self,message):
        super().__init__(message)
        self.message  = message
        
    def __str__(self):
        return self.message
        
class InvalidModelFile(Exception):
    
    def __init__(self,message):
        super().__init__(self,message)
        self.message = message
        
    def __str__(self):
        return self.message
    
        
class IncompleteInitialParameters(Exception):
    
    def __init__(self,**kwargs):
        super().__init__(self,kwargs['message'])
        self.message = kwargs['message']
        self.parameter = kwargs['param']
        
    def __str__(self):
        return self.message

class InvalidInputs(Exception):
    
    def __init__(self,message):
        super().__init__(self,message)
        self.message = message
        
    def __str__(self):
        return self.message
    