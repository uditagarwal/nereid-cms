#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import unittest2 as unittest

from trytond.config import CONFIG
CONFIG.options['db_type'] = 'sqlite'
from trytond.modules import register_classes
register_classes()

from nereid.testing import testing_proxy, TestCase
from trytond.transaction import Transaction


class TestBanner(TestCase):
    """Test Banners"""

    @classmethod
    def setUpClass(cls):
        super(TestBanner, cls).setUpClass()
        testing_proxy.install_module('nereid_cms')

    def setUp(self):
        self.banner_categ_obj = testing_proxy.pool.get(
            'nereid.cms.banner.category'
        )
        self.banner_obj = testing_proxy.pool.get('nereid.cms.banner')

    def test_0010_banner_categ(self):
        """All banners in published state.

        The banners attribute of the banner category returns all the banners
        irrespective of the status. The attribute published_banners must only
        return the active banners.

        This test creates four banner of which two are later archived, and the
        test ensures that there are only two published banners
        """
        with Transaction().start(testing_proxy.db_name,
            testing_proxy.user, None):

            banner_categ1 = self.banner_categ_obj.create({
                'name': 'CAT-A'
            })
            banner_categ2 = self.banner_categ_obj.create({
                'name': 'CAT-B'
            })
 
            self.banner_obj.create({
                'name': 'CAT-A1',
                'category': banner_categ1,
                'type': 'custom_code',
                'custom_code': 'Custom code A1',
                'state': 'archived'
            })
            self.banner_obj.create({
                'name': 'CAT-A2',
                'category': banner_categ1,
                'type': 'custom_code',
                'custom_code': 'Custom code A2',
                'state': 'published'
            })
            self.banner_obj.create({
                'name': 'CAT-B1',
                'category': banner_categ2,
                'type': 'custom_code',
                'custom_code': 'Custom code B1',
                'state': 'archived'
            })
            self.banner_obj.create({
                'name': 'CAT-B2',
                'category': banner_categ2,
                'type': 'custom_code',
                'custom_code': 'Custom code B2',
                'state': 'published'
            })

            categ1 = self.banner_categ_obj.browse(banner_categ1)
            categ2 = self.banner_categ_obj.browse(banner_categ2)
            self.assertEqual(len(categ1.banners), 2)
            self.assertEqual(len(categ2.banners), 2)
            self.assertEqual(len(categ1.published_banners), 1)
            self.assertEqual(len(categ2.published_banners), 1)

def suite():
    "Nereid CMS Banners test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestBanner)
        )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
