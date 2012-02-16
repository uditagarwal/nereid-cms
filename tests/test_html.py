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
from lxml import objectify


class TestGetHtml(TestCase):
    """Test Get Html for Banners
    """

    @classmethod
    def setUpClass(cls):
        super(TestGetHtml, cls).setUpClass()
        testing_proxy.install_module('nereid_cms')

    def setUp(self):
        self.banner_categ_obj = testing_proxy.pool.get(
            'nereid.cms.banner.category'
        )
        self.banner_obj = testing_proxy.pool.get('nereid.cms.banner')
        self.file_obj = testing_proxy.pool.get('nereid.static.file')
        self.folder_obj = testing_proxy.pool.get('nereid.static.folder')

    def test_0010_get_html(self):
        """
        Get Html for banners with type `image`.
        """
        with Transaction().start(
            testing_proxy.db_name, testing_proxy.user, None):

            banner_categ = self.banner_categ_obj.create({
                'name': 'Category A'
            })

            image = self.folder_obj.create({
                'name': 'image',
                'folder_name': 'image'
            })
            file = self.file_obj.create({
                'name': 'logo',
                'folder': image,
            })
            banner_id = self.banner_obj.create({
                'name': 'Test Banner1',
                'category': banner_categ,
                'type': 'image',
                'file': file,
                'state': 'published'
            })
            banner = self.banner_obj.browse(banner_id)
            rv = self.banner_obj.get_html(banner_id)
            html = objectify.fromstring(rv)
            self.assertEqual(html.find('img').get('src'), banner.file.id)

    def test_0020_get_html(self):
        """
        Get Html for banners with type `remote_image`.
        """
        with Transaction().start(
            testing_proxy.db_name, testing_proxy.user, None):

            banner_categ = self.banner_categ_obj.create({
                'name': 'Category B'
            })

            banner_id = self.banner_obj.create({
                'name': 'Test Banner2',
                'category': banner_categ,
                'type': 'remote_image',
                'remote_image_url': 'http://profile.ak.fbcdn.net/hprofile-ak-snc4/187819_122589627793765_7532740_n.jpg',
                'state': 'published'
            })
            banner = self.banner_obj.browse(banner_id)
            rv = self.banner_obj.get_html(banner_id)
            html = objectify.fromstring(rv)
            self.assertEqual(html.find('img').get('src'), banner.remote_image_url)

    def test_0030_get_html(self):
        """
        Get Html for banners with type `custom_code`.
        """
        with Transaction().start(
            testing_proxy.db_name, testing_proxy.user, None):

            banner_categ = self.banner_categ_obj.create({
                'name': 'Category C'
            })

            banner_id = self.banner_obj.create({
                'name': 'Test Banner3',
                'category': banner_categ,
                'type': 'custom_code',
                'custom_code': 'Custom code for Test Banner3',
                'state': 'published'
            })
            banner = self.banner_obj.browse(banner_id)
            rv = self.banner_obj.get_html(banner_id)
            self.assertEqual(rv, banner.custom_code)

def suite():
    "Catalog Browse Node test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestGetHtml)
        )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
