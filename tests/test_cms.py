#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from ast import literal_eval
import unittest2 as unittest

from trytond.config import CONFIG
CONFIG.options['db_type'] = 'sqlite'
from trytond.modules import register_classes
register_classes()

from nereid.testing import testing_proxy
from trytond.transaction import Transaction


class TestCMS(unittest.TestCase):
    """Test CMS"""

    @classmethod
    def setUpClass(cls):
        testing_proxy.install_module('nereid_cms')

        article_categ_obj = testing_proxy.pool.get('nereid.article.category')
        article_obj = testing_proxy.pool.get('nereid.cms.article')

        with Transaction().start(testing_proxy.db_name, 1, None) as txn:
            company = testing_proxy.create_company('Test Company')
            cls.guest_user = testing_proxy.create_guest_user()

            article_category_template = testing_proxy.create_template(
                'article-category.jinja', ' ')
            article_template = testing_proxy.create_template(
                'article.jinja', 
                ''' Here is a test article. 
                Here goes the text from source {{ article.content }}''')
            cls.site = testing_proxy.create_site('testsite.com')

            cls.article_categ = article_categ_obj.create({
                'title': 'Test Categ',
                'unique_name': 'test-categ',
                'template': article_category_template,
            })

            cls.article = article_obj.create({
                'title': 'Test Article',
                'uri': 'test-article',
                'template': article_template,
                'content': ' This is nereid test article. ',
                'sequence': 10,
                'category': cls.article_categ,
            })

            testing_proxy.create_template(
                'home.jinja', 
                '{{request.nereid_website.get_currencies()}}',
                cls.site)
            txn.cursor.commit()

    def get_app(self):
        return testing_proxy.make_app(
            SITE='testsite.com', 
            GUEST_USER=self.guest_user)

    def setUp(self):
        self.currency_obj = testing_proxy.pool.get('currency.currency')
        self.site_obj = testing_proxy.pool.get('nereid.website')

    def test_0010_article_category(self):
        "Successful rendering of an article_category page"
        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/en_US/article-category/test-categ')
            self.assertEqual(response.status_code, 200)

    def test_0020_article(self):
        "Successful rendering of an article page"
        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/en_US/article/test-article')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data,
                ''' Here is a test article. 
                Here goes the text from source  This is nereid test article. ''')

def suite():
    "CMS test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCMS)
        )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
