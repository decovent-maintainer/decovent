""" Test memoization """

import unittest
from test import *
from decovent import *


class Mouse(object):
    def __init__(self):
        self.on_click()
        
    @raise_event(memoize_=True)
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point
           
    @set_handler('click', memoize_=True)
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point


class test_12(unittest.TestCase):   
    def test(self):
        mouse = Mouse()

        e, h = mouse.click(10, 20)
        check_error(e, h)
        
        e_success, e_result, e_class, e_meth = e
        hash_ = str(hash(e_class)) + str(hash(e_meth)) + '_' + e_meth.func_name
        self.assertEqual(hash_ in decovent._memoize, True)
        
        self.assertEqual(len(h), 1)
        
        for h_success, h_result, h_class, h_meth in h:
            hash_ = str(hash(h_class)) + str(hash(h_meth)) + '_' + h_meth.func_name

            if decovent.asynchronous == True:
                #allows time for asynchronous threads to finish  
                import time     
                time.sleep(.3)
                
            self.assertEqual(hash_ in decovent._memoize, True)