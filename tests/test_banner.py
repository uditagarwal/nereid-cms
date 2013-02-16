# -*- coding: utf-8 -*-
'''

    nereid_cms test_banner

    :copyright: (c) 2010-2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
import unittest

from lxml import objectify
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction


class TestBanner(NereidTestCase):
    """Test Banners"""

    def setUp(self):
        trytond.tests.test_tryton.install_module('nereid_cms')

        self.currency_obj = POOL.get('currency.currency')
        self.site_obj = POOL.get('nereid.website')
        self.banner_categ_obj = POOL.get('nereid.cms.banner.category')
        self.banner_obj = POOL.get('nereid.cms.banner')
        self.folder_obj = POOL.get('nereid.static.folder')
        self.file_obj = POOL.get('nereid.static.file')
        self.company_obj = POOL.get('company.company')
        self.nereid_user_obj = POOL.get('nereid.user')
        self.url_map_obj = POOL.get('nereid.url_map')
        self.language_obj = POOL.get('ir.lang')
        self.nereid_website_obj = POOL.get('nereid.website')

        self.templates = {
            'localhost/home.jinja':
                '''{% for banner in get_banner_category("test-banners").banners %}
                {{ banner.get_html(banner.id)|safe }}
                {% endfor %}
                ''',
        }

    def get_template_source(self, name):
        """
        Return templates
        """
        return self.templates.get(name)

    def setup_defaults(self):
        """
        Setup the defaults
        """
        usd = self.currency_obj.create({
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        })
        company_id = self.company_obj.create({
            'name': 'Openlabs',
            'currency': usd
        })
        guest_user = self.nereid_user_obj.create({
            'name': 'Guest User',
            'display_name': 'Guest User',
            'email': 'guest@openlabs.co.in',
            'password': 'password',
            'company': company_id,
        })
        self.registered_user_id = self.nereid_user_obj.create({
            'name': 'Registered User',
            'display_name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': company_id,
        })

        # Create website
        url_map_id, = self.url_map_obj.search([], limit=1)
        en_us, = self.language_obj.search([('code', '=', 'en_US')])
        return self.nereid_website_obj.create({
            'name': 'localhost',
            'url_map': url_map_id,
            'company': company_id,
            'application_user': USER,
            'default_language': en_us,
            'guest_user': guest_user,
            'currencies': [('set', [usd])],
        })

    def test_0010_banner_categ(self):
        """All banners in published state.

        The banners attribute of the banner category returns all the banners
        irrespective of the status. The attribute published_banners must only
        return the active banners.

        This test creates four banner of which two are later archived, and the
        test ensures that there are only two published banners
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):

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
        with Transaction().start(DB_NAME, USER, CONTEXT):
            site = self.setup_defaults()

            category = self.banner_categ_obj.create({
                'name': 'test-banners',
                'website': site
            })
            folder_id = self.folder_obj.create({
                'description': 'image',
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

            app = self.get_app()
            with app.test_client() as c:
                response = c.get('/en_US/')
                html = objectify.fromstring(response.data)
                self.assertEqual(
                    html.find('img').get('src'),
                    '/en_US/static-file/image/logo'
                )

    def test_0030_remote_image(self):
        """
        Test the remote image type banner
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):
            site = self.setup_defaults()

            category = self.banner_categ_obj.create({
                'name': 'test-banners',
                'website': site
            })
            banner_id = self.banner_obj.create({
                'name': 'Test Remote Image Banner',
                'category': category,
                'type': 'remote_image',
                'remote_image_url': 'http://some/remote/url',
                'state': 'published'
            })

            app = self.get_app()
            with app.test_client() as c:
                response = c.get('/en_US/')
                html = objectify.fromstring(response.data)
                self.assertEqual(
                    html.find('img').get('src'),
                    'http://some/remote/url'
                )

    def test_0040_custom_code(self):
        """
        Test the custom code
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):
            site = self.setup_defaults()

            category = self.banner_categ_obj.create({
                'name': 'test-banners',
                'website': site
            })
            banner_id = self.banner_obj.create({
                'name': 'Test Remote Image Banner',
                'category': category,
                'type': 'custom_code',
                'custom_code': 'some ultra complex custom code',
                'state': 'published'
            })

            app = self.get_app()
            with app.test_client() as c:
                response = c.get('/en_US/')
                self.assertTrue(
                    'some ultra complex custom code' in response.data,
                )


class TestGetHtml(NereidTestCase):
    """Test Get Html for Banners
    """

    def setUp(self):
        trytond.tests.test_tryton.install_module('nereid_cms')

        self.currency_obj = POOL.get('currency.currency')
        self.banner_obj = POOL.get('nereid.cms.banner')
        self.banner_categ_obj = POOL.get('nereid.cms.banner.category')
        self.file_obj = POOL.get('nereid.static.file')
        self.folder_obj = POOL.get('nereid.static.folder')
        self.folder_obj = POOL.get('nereid.static.folder')
        self.file_obj = POOL.get('nereid.static.file')
        self.company_obj = POOL.get('company.company')
        self.nereid_user_obj = POOL.get('nereid.user')
        self.url_map_obj = POOL.get('nereid.url_map')
        self.language_obj = POOL.get('ir.lang')
        self.nereid_website_obj = POOL.get('nereid.website')

        self.templates = {
            'localhost/home.jinja':
                '''{% for b in get_banner_category('Category A').banners -%}
                {{ b.get_html(b.id)|safe }}
                {%- endfor %}
                ''',
            'localhost/article-category.jinja': '{{ articles|length }}',
            'localhost/article.jinja': '{{ article.content }}',
        }

    def get_template_source(self, name):
        """
        Return templates
        """
        return self.templates.get(name)

    def setup_defaults(self):
        """
        Setup the defaults
        """
        usd = self.currency_obj.create({
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        })
        company_id = self.company_obj.create({
            'name': 'Openlabs',
            'currency': usd
        })
        guest_user = self.nereid_user_obj.create({
            'name': 'Guest User',
            'display_name': 'Guest User',
            'email': 'guest@openlabs.co.in',
            'password': 'password',
            'company': company_id,
        })
        self.registered_user_id = self.nereid_user_obj.create({
            'name': 'Registered User',
            'display_name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': company_id,
        })

        # Create website
        url_map_id, = self.url_map_obj.search([], limit=1)
        en_us, = self.language_obj.search([('code', '=', 'en_US')])
        return self.nereid_website_obj.create({
            'name': 'localhost',
            'url_map': url_map_id,
            'company': company_id,
            'application_user': USER,
            'default_language': en_us,
            'guest_user': guest_user,
            'currencies': [('set', [usd])],
        })

    def test_0010_get_html(self):
        """
        Get Html for banners with type `image`.
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):
            site = self.setup_defaults()

            banner_categ = self.banner_categ_obj.create({
                'name': 'Category A',
                'website': site,
            })

            image = self.folder_obj.create({
                'description': 'image',
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

            app = self.get_app()
            with app.test_client() as c:
                rv = c.get('/')
                html = objectify.fromstring(rv.data)
                self.assertEqual(
                    html.find('img').get('src'), '/en_US/static-file/image/logo'
                )

    def test_0020_get_html(self):
        """
        Get Html for banners with type `remote_image`.
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):
            site = self.setup_defaults()

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
        with Transaction().start(DB_NAME, USER, CONTEXT):
            site = self.setup_defaults()

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
    "Nereid CMS Banners test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(TestBanner),
        unittest.TestLoader().loadTestsFromTestCase(TestGetHtml),
    ])
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
