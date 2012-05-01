# -*- coding: utf-8 -*-
'''
    
    nereid_cms test_cms
    
    :copyright: (c) 2010-2012 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
    
'''
import unittest2 as unittest

from trytond.config import CONFIG
CONFIG.options['db_type'] = 'sqlite'
from trytond.modules import register_classes
register_classes()

from nereid.testing import testing_proxy, TestCase
from trytond.transaction import Transaction


class TestCMS(TestCase):
    """Test CMS"""

    @classmethod
    def setUpClass(cls):
        super(TestCMS, cls).setUpClass()
        testing_proxy.install_module('nereid_cms')

        article_categ_obj = testing_proxy.pool.get(
            'nereid.cms.article.category'
            )
        article_obj = testing_proxy.pool.get('nereid.cms.article')

        with Transaction().start(testing_proxy.db_name, 1, None) as txn:
            company = testing_proxy.create_company('Test Company')
            cls.guest_user = testing_proxy.create_guest_user(company=company)

            article_category_template = testing_proxy.create_template(
                'article-category.jinja', ' ')
            cls.article_template = ''' Here is a test article. 
                Here goes the text from source {{ article.content }}'''
            article_template = testing_proxy.create_template(
                'article.jinja', cls.article_template
            )
            cls.site = testing_proxy.create_site('localhost',
                application_user = 1, guest_user = cls.guest_user
            )

            cls.article_categ = article_categ_obj.create({
                'title': 'Test Categ',
                'unique_name': 'test-categ',
                'template': article_category_template,
            })

            cls.article_content = ' This is nereid test article. '
            cls.article = article_obj.create({
                'title': 'Test Article',
                'uri': 'test-article',
                'template': article_template,
                'content': cls.article_content,
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
            SITE='localhost'
        )

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
            expected_op = self.article_template.replace(
                '{{ article.content }}', self.article_content
            )
            self.assertEqual(response.data, expected_op)


def suite():
    "CMS test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCMS)
        )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
