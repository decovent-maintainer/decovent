""" Test integration with custom decorators """

import unittest
from test import *
from decovent import *

authorizations = ['do_click', 'do_move']

class authorize(object):  
    """ Authorization check decorator """
    def __init__(self, auth_object):
        self.auth_object = auth_object
        
    def __call__(self, f):
        def auth_f(*args, **kwargs):
            if self.auth_object in authorizations:
                return f(*args, **kwargs)
            else:
                raise ValueError('Unauthorized')
        return auth_f
    
class Mouse(object):
    @classmethod
    @authorize('do_click')            
    @raise_event()
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point

    @classmethod
    @authorize('do_click')               
    @set_handler('click')
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point


class test_14(unittest.TestCase):   
    def test(self):
        Mouse.on_click()
        e, h = Mouse.click(10, 20)
        check_error(e, h)
        
        e_success, e_result, e_class, e_meth = e
        self.assertEqual(e_success, True)
        self.assertEqual(e_result, Point(10, 20))
        
        self.assertEqual(len(h), 1)
        
        for h_success, h_result, h_class, h_meth in h:
            if decovent.asynchronous == False:
                self.assertEqual(h_success, True)
                self.assertEqual(h_result, Point(10, 20))            
            else:
                self.assertEqual(None, h_success)
                self.assertEqual(None, h_result)