# -*- coding: utf-8 -*-
'''
    
    nereid_cms xml_test_runner
    
    :copyright: (c) 2010-2012 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
    
'''
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
