""" Test multiple handlers and events of another class """

import unittest
from test import *
from decovent import *


class Mouse(object):
    def __init__(self):
        self.on_click()
        self.on_move()
        self.on_right_click()

    @raise_event()
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point

    @raise_event()
    def move(self, x, y):
        self.point = Point(x, y)
        return self.point
    
    @raise_event()
    def right_click(self, x, y):
        self.point = Point(x, y)
        return self.point

    @set_handler('click')
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point
    
    @set_handler('move')
    def on_move(self, x, y):
        self.point = Point(x, y)
        return self.point
    
    @set_handler('right_click')
    def on_right_click(self, x, y):
        raise TypeError('Wrong values')

        
class Screen(object):           
    @set_handler('click', Mouse)
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point

    @set_handler('move', Mouse)
    def on_move(self, x, y):
        self.point = Point(x, y)
        return self.point
    
    @set_handler('right_click', Mouse)
    def on_right_click(self, x, y):
        raise TypeError('Wrong values')

    
class test_03(unittest.TestCase):   
    def test(self):
        mouse = Mouse()
        screen = Screen()
        screen.on_click()
        screen.on_move()
        screen.on_right_click()


        e, h = mouse.click(10, 20)
        check_error(e, h)
        
        e_success, e_result, e_class, e_meth = e        
        self.assertEqual(e_success, True)
        self.assertEqual(e_result, Point(10, 20))
        
        self.assertEqual(len(h), 2)
        
        for h_success, h_result, h_class, h_meth in h:
            if decovent.asynchronous == False:
                self.assertEqual(h_success, True)
                self.assertEqual(h_result, Point(10, 20))            
            else:
                self.assertEqual(None, h_success)
                self.assertEqual(None, h_result)  
                
                
                
        e, h = mouse.move(10, 20)
        check_error(e, h)
        
        e_success, e_result, e_class, e_meth = e        
        self.assertEqual(e_success, True)
        self.assertEqual(e_result, Point(10, 20))
        
        self.assertEqual(len(h), 2)
        
        for h_success, h_result, h_class, h_meth in h:
            if decovent.asynchronous == False:
                self.assertEqual(h_success, True)
                self.assertEqual(h_result, Point(10, 20))            
            else:
                self.assertEqual(None, h_success)
                self.assertEqual(None, h_result)                  
                
                
                
        e, h = mouse.right_click(10, 20)
        
        e_success, e_result, e_class, e_meth = e        
        self.assertEqual(e_success, True)
        self.assertEqual(e_result, Point(10, 20))
        
        self.assertEqual(len(h), 2)
        
        for h_success, h_result, h_class, h_meth in h:
            if decovent.asynchronous == False:
                self.assertEqual(h_success, False)
                self.assertEqual(isinstance(h_result, TypeError), True)            
            else:
                self.assertEqual(None, h_success)
                self.assertEqual(None, h_result)                                  