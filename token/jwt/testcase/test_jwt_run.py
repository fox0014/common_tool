# -*-coding:utf-8 -*-
import unittest
from test_jwt001 import TestStringMethods


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestStringMethods('test_jwt_token'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())