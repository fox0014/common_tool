import sys
sys.path.append("../")


import myjwttest
import unittest


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        print('begin')

    def tearDown(self):
        print('clean')

    def test_jwt_token(self):
        _test_data = {'name': 'xiongxiong'}
        create_data = myjwttest.create_jwt_token(data=_test_data)
        decrypt_data = myjwttest.decrypt_jwt_token(encoded=create_data)
        self.assertEqual(_test_data, decrypt_data)



if __name__ == '__main__':
    unittest.main()