""" Test @classmethods """

import unittest
from test import *
from decovent import *


class Mouse(object):

    @raise_event()
    def click(self, x, y):
        self.point = Point(x, y)
        return self.point

    @classmethod
    @set_handler('click')
    def on_click(self, x, y):
        self.point = Point(x, y)
        return self.point


class test_05(unittest.TestCase):

    def test(self):
        Mouse.on_click()
        mouse = Mouse()

        (e, h) = mouse.click(10, 20)
        check_error(e, h)

        (e_success, e_result, e_class, e_meth) = e
        self.assertEqual(e_success, True)
        self.assertEqual(e_result, Point(10, 20))

        self.assertEqual(len(h), 1)

        for (h_success, h_result, h_class, h_meth) in h:
            if decovent.default_context.asynchronous is False:
                self.assertEqual(h_success, True)
                self.assertEqual(h_result, Point(10, 20))
            else:
                self.assertEqual(None, h_success)
                self.assertEqual(None, h_result)
