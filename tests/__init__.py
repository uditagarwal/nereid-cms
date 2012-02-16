#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import unittest2 as unittest

from test_cms import TestCMS
from test_banner import TestBanner
from test_menu_for import TestMenuFor


def suite():
    "CMS test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestBanner)
    )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCMS)
    )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestMenuFor)
    )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
