#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import unittest2 as unittest

from lxml import objectify
from trytond.config import CONFIG
CONFIG.options['db_type'] = 'sqlite'
CONFIG.options['data_path'] = '/tmp/temp_tryton_data/'
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
        with Transaction().start(testing_proxy.db_name, 1, None) as txn:
            cls.company = testing_proxy.create_company('Test Company')
            cls.guest_user = testing_proxy.create_guest_user(
                company=cls.company
            )
            cls.site = testing_proxy.create_site(
                'localhost', guest_user=cls.guest_user
            )
            testing_proxy.create_template(
                'home.jinja',
                '''{% for banner in get_banner_category("test-banners").banners %}
                {{ banner.get_html(banner.id)|safe }}
                {% endfor %}
                ''', cls.site)
            txn.cursor.commit()

    def setUp(self):
        self.banner_categ_obj = testing_proxy.pool.get(
            'nereid.cms.banner.category'
        )
        self.banner_obj = testing_proxy.pool.get('nereid.cms.banner')
        self.folder_obj = testing_proxy.pool.get('nereid.static.folder')
        self.file_obj = testing_proxy.pool.get('nereid.static.file')

    def get_app(self):
        return testing_proxy.make_app(SITE='localhost')

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

    def test_0020_banner_image(self):
        """
        Test the image type banner created using static files
        """
        with Transaction().start(testing_proxy.db_name,
                    testing_proxy.user, None) as txn:
            category = self.banner_categ_obj.create({
                'name': 'test-banners',
                'website': self.site
            })
            folder_id = self.folder_obj.create({
                'name': 'image',
                'folder_name': 'image'
            })
            file_id = self.file_obj.create({
                'name': 'logo',
                'folder': folder_id,
            })
            banner_id = self.banner_obj.create({
                'name': 'Test Image Banner',
                'category': category,
                'type': 'image',
                'file': file_id,
                'state': 'published'
            })
            txn.cursor.commit()

        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/en_US/')
            html = objectify.fromstring(response.data)
            self.assertEqual(
                html.find('img').get('src'),
                '/en_US/static-files/image/logo'
            )

        # Delete the banners
        with Transaction().start(testing_proxy.db_name,
                    testing_proxy.user, None) as txn:
            self.banner_obj.delete(banner_id)
            self.banner_categ_obj.delete(category)
            txn.cursor.commit()

    def test_0030_remote_image(self):
        """
        Test the remote image type banner
        """
        with Transaction().start(testing_proxy.db_name,
                    testing_proxy.user, None) as txn:
            category = self.banner_categ_obj.create({
                'name': 'test-banners',
                'website': self.site
            })
            banner_id = self.banner_obj.create({
                'name': 'Test Remote Image Banner',
                'category': category,
                'type': 'remote_image',
                'remote_image_url': 'http://some/remote/url',
                'state': 'published'
            })
            txn.cursor.commit()

        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/en_US/')
            html = objectify.fromstring(response.data)
            self.assertEqual(
                html.find('img').get('src'),
                'http://some/remote/url'
            )

        # Delete the banners
        with Transaction().start(testing_proxy.db_name,
                    testing_proxy.user, None) as txn:
            self.banner_obj.delete(banner_id)
            self.banner_categ_obj.delete(category)
            txn.cursor.commit()

    def test_0040_custom_code(self):
        """
        Test the custom code
        """
        with Transaction().start(testing_proxy.db_name,
                    testing_proxy.user, None) as txn:
            category = self.banner_categ_obj.create({
                'name': 'test-banners',
                'website': self.site
            })
            banner_id = self.banner_obj.create({
                'name': 'Test Remote Image Banner',
                'category': category,
                'type': 'custom_code',
                'custom_code': 'some ultra complex custom code',
                'state': 'published'
            })
            txn.cursor.commit()

        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/en_US/')
            self.assertTrue(
                'some ultra complex custom code' in response.data,
            )

        # Delete the banners
        with Transaction().start(testing_proxy.db_name,
                    testing_proxy.user, None) as txn:
            self.banner_obj.delete(banner_id)
            self.banner_categ_obj.delete(category)
            txn.cursor.commit()


def suite():
    "Nereid CMS Banners test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestBanner)
        )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
