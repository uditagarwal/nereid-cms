# -*- coding: utf-8 -*-
"""
    __init__

    Collect all tests here

    :copyright: © 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest

from .test_banner import TestBanner
from .test_cms import TestCMS
from .test_view_depends import TestViewDepends
from .test_menu_for import TestMenuFor


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(TestBanner),
        unittest.TestLoader().loadTestsFromTestCase(TestCMS),
        unittest.TestLoader().loadTestsFromTestCase(TestMenuFor),
        unittest.TestLoader().loadTestsFromTestCase(TestViewDepends)
    ])
    return test_suite
