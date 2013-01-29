""" Test if a handler registered multiple times is executed only once """

import unittest
from test import *
from decovent import *


class Mouse(object):
    def __init__(self):
        self.on_click()         # register the handler for the first time
        self.on_click()         # register the handler for the second time
        self.on_click()         # register the handler for the third time
        
    @raise_event()
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point
           
    @set_handler('click')
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point


class test_02(unittest.TestCase):   
    def test(self):
        mouse = Mouse()

        e, h = mouse.click(10, 20)  
        check_error(e, h)
        self.assertEqual(len(h), 1) # handler was executed only once        