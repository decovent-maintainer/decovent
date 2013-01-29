""" Test functions and classic classes """

import unittest
from test import *
from decovent import *


class Mouse:    
    @raise_event()
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point
    
    @set_handler('click')
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point
    
@set_handler('click', Mouse)
def on_click(x, y):
    self.point = Point(x, y)
    return self.point


class test_08(unittest.TestCase):
    def test(self):
        
        mouse = Mouse()
        
        #we can't do self.assertRaises(TypeError, self.mouse.on_click())
        #because the error is raised by the decorator not the method  
        #itself and the actual callable will never be inspected  

        try:
            mouse.on_click()
        except Exception as e:
            self.assertEqual(type(e), TypeError)

        #same here
        try:
            mouse.click(10, 20)
        except Exception as e:
            self.assertEqual(type(e), TypeError)

        #same here
        try:
            on_click()
        except Exception as e:
            self.assertEqual(type(e), TypeError)
            