""" Test if an handler will be unregistered after its first execution """

import unittest
from test import *
from decovent import *


class Mouse(object):
    def __init__(self):
        self.on_click()
        
    @raise_event()
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point
           
    @set_handler('click', unregister=True)
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point


class test_10(unittest.TestCase):   
    def test(self):
        mouse = Mouse()
        e, h = mouse.click(10, 20)
        check_error(e, h)
        self.assertEqual(len(h), 1)
        
        e, h = mouse.click(30, 40)
        check_error(e, h)
        self.assertEqual(len(h), 0)