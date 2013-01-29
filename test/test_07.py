""" Test @staticmethods """

import unittest
from test import *
from decovent import *


class Mouse(object):
    @staticmethod
    @raise_event()
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point
    
    @staticmethod
    @set_handler('click')
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point
    

class test_07(unittest.TestCase):
    def test(self):
    
        #we can't do self.assertRaises(TypeError, Mouse.on_click())
        #because the error is raised by the decorator not the method  
        #itself and the actual callable will never be inspected  

        try:
            Mouse.on_click()
        except Exception as e:
            self.assertEqual(type(e), TypeError)

        #same here
        try:
            Mouse.click(10, 20)
        except Exception as e:
            self.assertEqual(type(e), TypeError)
            