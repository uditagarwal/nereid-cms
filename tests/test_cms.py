# -*- coding: utf-8 -*-
'''

    nereid_cms test_cms

    :copyright: (c) 2010-2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT, \
    test_view, test_depends
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction


class TestCMS(NereidTestCase):
    """Test CMS"""

    def setUp(self):
        trytond.tests.test_tryton.install_module('nereid_cms')

        self.currency_obj = POOL.get('currency.currency')
        self.site_obj = POOL.get('nereid.website')
        self.article_category_obj = POOL.get('nereid.cms.article.category')
        self.article_obj = POOL.get('nereid.cms.article')
        self.folder_obj = POOL.get('nereid.static.folder')
        self.file_obj = POOL.get('nereid.static.file')
        self.company_obj = POOL.get('company.company')
        self.nereid_user_obj = POOL.get('nereid.user')
        self.url_map_obj = POOL.get('nereid.url_map')
        self.language_obj = POOL.get('ir.lang')
        self.nereid_website_obj = POOL.get('nereid.website')
        self.ArticleAttribute = POOL.get('nereid.cms.article.attribute')

        self.templates = {
            'localhost/home.jinja':
            '''{% for banner in get_banner_category("test-banners").banners %}
            {{ banner.get_html(banner.id)|safe }}
            {% endfor %}
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
        self.nereid_website_obj.create({
            'name': 'localhost',
            'url_map': url_map_id,
            'company': company_id,
            'application_user': USER,
            'default_language': en_us,
            'guest_user': guest_user,
            'currencies': [('set', [usd])],
        })

        # Create an article category
        article_categ = self.article_category_obj.create({
            'title': 'Test Categ',
            'unique_name': 'test-categ',
        })

        self.article_obj.create({
            'title': 'Test Article',
            'uri': 'test-article',
            'content': 'Test Content',
            'sequence': 10,
            'category': article_categ,
        })

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('nereid_cms')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test_0010_article_category(self):
        "Successful rendering of an article_category page"
        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()
            with app.test_client() as c:
                response = c.get('/en_US/article-category/test-categ')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, '1')

    def test_0020_article(self):
        "Successful rendering of an article page"
        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()
            with app.test_client() as c:
                response = c.get('/en_US/article/test-article')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, 'Test Content')

    def test_0030_sitemapindex(self):
        '''
        Successful index rendering
        '''
        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app(DEBUG=True)
            with app.test_client() as c:
                response = c.get('/en_US/sitemaps/article-category-index.xml')
                self.assertEqual(response.status_code, 200)

    def test_0040_category_sitemap(self):
        '''
        Successful rendering artical catagory sitemap
        '''
        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()
            with app.test_client() as c:
                response = c.get('en_US/sitemaps/article-category-1.xml')
                self.assertEqual(response.status_code, 200)

    def test_0050_article_attribute(self):
        '''
        Test creating and deleting an Article with attributes
        '''
        with Transaction().start(DB_NAME, USER, CONTEXT):
            article_category = self.article_category_obj.create({
                'title': 'Test Categ',
                'unique_name': 'test-categ',
            })

            article1 = self.article_obj.create({
                'title': 'Test Article',
                'uri': 'test-article',
                'content': 'Test Content',
                'sequence': 10,
                'category': article_category,
                'attributes': [
                    ('create', {
                        'name': 'google+',
                        'value': 'abc',
                    })
                ]
            })
            # Checks an article is created with attributes
            self.assert_(article1.id)
            self.assertEqual(self.ArticleAttribute.search([], count=True), 1)
            # Checks that if an article is deleted then respective attributes
            # are also deleted.
            self.article_obj.delete([article1])
            self.assertEqual(self.ArticleAttribute.search([], count=True), 0)


def suite():
    "CMS test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCMS)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
