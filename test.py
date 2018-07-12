#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import performance_data


class PerformanceDataTest(unittest.TestCase):
    def tearDown(self):
        pass

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_product_info(self):
        product_list = performance_data.get_product_info()
        self.assertEqual(len(product_list), 12)


if __name__ == '__main__':
    unittest.main()