#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import unittest2 as unittest
from nereid.contrib.testing import xmlrunner

from test_cms import TestCMS
from test_banner import TestBanner
from test_menu_for import TestMenuFor
from test_html import TestGetHtml


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
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestGetHtml)
    )
    return suite

if __name__ == '__main__':
    with open('result.xml', 'wb') as stream:
        xmlrunner.XMLTestRunner(stream).run(suite())
