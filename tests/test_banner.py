#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import unittest2 as unittest

from trytond.config import CONFIG
CONFIG.options['db_type'] = 'sqlite'
from trytond.modules import register_classes
register_classes()

from nereid.testing import testing_proxy
from trytond.transaction import Transaction


class TestBanner(unittest.TestCase):
    """Test Banners"""

    @classmethod
    def setUpClass(cls):
        testing_proxy.install_module('nereid_cms')

    def setUp(self):
        self.banner_categ_obj = testing_proxy.pool.get('nereid.cms.banner.category')
        self.banner_obj = testing_proxy.pool.get('nereid.cms.banner')

    def test_0010_banner_categ(self):
        """All banners in published state
        """
        with Transaction().start(testing_proxy.db_name,
            testing_proxy.user, None):

            banner_categ1 = self.banner_categ_obj.create({
                'name': 'CAT-A'
            })
            banner_categ2 = self.banner_categ_obj.create({
                'name': 'CAT-B'
            })

            banner1 = self.banner_obj.create({
                'name': 'CAT-A1',
                'category': banner_categ1,
                'type': 'custom_code',
                'custom_code': 'Custom code A1',
                'state': 'published'
            })
            banner2 = self.banner_obj.create({
                'name': 'CAT-A2',
                'category': banner_categ1,
                'type': 'custom_code',
                'custom_code': 'Custom code A2',
                'state': 'published'
            })
            banner3 = self.banner_obj.create({
                'name': 'CAT-B1',
                'category': banner_categ2,
                'type': 'custom_code',
                'custom_code': 'Custom code B1',
                'state': 'published'
            })
            banner4 = self.banner_obj.create({
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
            self.assertEqual(len(categ1.published_banners), 2)
            self.assertEqual(len(categ2.published_banners), 2)

    def test_0020_banner_categ(self):
        with Transaction().start(testing_proxy.db_name,
            testing_proxy.user, None):

            banner_categ1 = self.banner_categ_obj.create({
                'name': 'CAT-A'
            })
            banner_categ2 = self.banner_categ_obj.create({
                'name': 'CAT-B'
            })

            banner1 = self.banner_obj.create({
                'name': 'CAT-A1',
                'category': banner_categ1,
                'type': 'custom_code',
                'custom_code': 'Custom code A1',
                'state': 'archived'
            })
            banner2 = self.banner_obj.create({
                'name': 'CAT-A2',
                'category': banner_categ1,
                'type': 'custom_code',
                'custom_code': 'Custom code A2',
                'state': 'published'
            })
            banner3 = self.banner_obj.create({
                'name': 'CAT-B1',
                'category': banner_categ2,
                'type': 'custom_code',
                'custom_code': 'Custom code B1',
                'state': 'archived'
            })
            banner4 = self.banner_obj.create({
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
    "Catalog Browse Node test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestBanner)
        )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
