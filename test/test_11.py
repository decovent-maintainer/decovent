""" Test if handlers are unregistered using decovent.reset """

import unittest
from test import *
from decovent import *


class Mouse(object):
    def __init__(self):
        self.on_click()
        self.on_move()
        
    @raise_event()
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point
           
    @raise_event()
    def move(self, x, y):
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
    

class test_11(unittest.TestCase):   
    def test(self):
        mouse = Mouse()
        
        m_hash = hash(Mouse)                
        decovent.reset(Mouse, 'click')
        
        handlers = decovent._local.events[m_hash]
        for event, class_, handler, unregister, memoize, timeout in handlers:
            self.assertNotEqual(event, 'click')  
        
        decovent.reset(Mouse)
        self.assertFalse(m_hash in decovent._local.events)