""" Test method execution timeout """

import unittest
from time import sleep
from test import *
from decovent import *


class Mouse(object):
    def __init__(self):
        self.on_click()
            
    @raise_event(timeout=.2)
    def click(self, x, y):
        sleep(1)
        self.point = Point(x, y)
        return self.point

    @set_handler('click', timeout=.2)
    def on_click(self, x, y):
        sleep(1)
        self.point = Point(x, y)
        return self.point


class test_13(unittest.TestCase):   
    def test(self):
        mouse = Mouse()
        e, h = mouse.click(10, 20)        
        
        e_success, e_result, e_class, e_meth = e
        self.assertEqual(e_success, False)
        
        self.assertEqual(len(h), 1)
        
        for h_success, h_result, h_class, h_meth in h:
            if decovent.asynchronous == False:
                self.assertEqual(h_success, False)
                result = h_result
                if decovent.exc_info == True:
                    result = h_result[1]            
                self.assertEqual(isinstance(result, RuntimeError), True)
            else:
                self.assertEqual(None, h_success)
                self.assertEqual(None, h_result)