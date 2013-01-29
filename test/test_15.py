""" Test the number of active methods """

import unittest
from time import sleep
from test import *
from decovent import *

class Mouse(object):
    def __init__(self):
        self.on_click_01()
        self.on_click_02()
        self.on_click_03()
        
    @raise_event()
    def click(self, x, y):
        sleep(1.5)
        self.point = Point(x, y)
        return self.point
           
    @set_handler('click')
    def on_click_01(self, x, y):
        assert decovent._active._Semaphore__value == 2
        sleep(1)
        self.point = Point(x, y)
        return self.point    

    @set_handler('click')
    def on_click_02(self, x, y):
        assert decovent._active._Semaphore__value == 1
        sleep(.5)
        self.point = Point(x, y)
        return self.point    

    @set_handler('click')
    def on_click_03(self, x, y):
        assert decovent._active._Semaphore__value == 0
        self.point = Point(x, y)
        return self.point
    

class test_15(unittest.TestCase):   
    def test(self):        
        mouse = Mouse()
        e, h = mouse.click(10, 20)
        check_error(e, h)