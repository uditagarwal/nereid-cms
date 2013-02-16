# -*- coding: utf-8 -*-
'''

    nereid_cms test_menu_for

    :copyright: (c) 2010-2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
import unittest
from ast import literal_eval

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction


class TestMenuFor(NereidTestCase):
    """Test menu_for"""

    @classmethod
    def setUpClass(cls):
        super(TestMenuFor, cls).setUpClass()
        testing_proxy.install_module('nereid_cms')
        testing_proxy.install_module('product')

        with Transaction().start(testing_proxy.db_name, 1, None) as txn:
            menu_obj = Pool().get('nereid.cms.menu')
            website_obj = Pool().get('nereid.website')
            url_obj = Pool().get('nereid.url_map')
            language_obj = Pool().get('ir.lang')
            model_obj = Pool().get('ir.model')
            model_field_obj = Pool().get('ir.model.field')
            prod_categ_obj = Pool().get('product.category')
            article_categ_obj = Pool().get('nereid.cms.article.category')
            article_obj = testing_proxy.pool.get('nereid.cms.article')

            # Create company
            cls.company = testing_proxy.create_company('Test Company')
            cls.guest_user = testing_proxy.create_guest_user(company=cls.company)

            url_map = url_obj.create({
                'name': 'Default'
            })
            language, = language_obj.search([
                ('code', '=', 'en_US')
            ])
            prod_categ = prod_categ_obj.create({
                'name': 'Category1'
            })
            category_id = prod_categ_obj.search([
                ('name', '=', 'Category1')
            ])
            cls.site1 = testing_proxy.create_site('localhost',
                application_user = 1, guest_user=cls.guest_user
            )
            cls.site2 = testing_proxy.create_site('test_site2',
                application_user = 1, guest_user=cls.guest_user
            )
            model = model_obj.search([
                ('model', '=', 'product.category')
            ])
            fields = model_field_obj.search([
                ('ttype', '=', 'char'),
                ('model', '=', model[0])
            ])
            children_field = model_field_obj.search([
                ('ttype', '=', 'one2many'),
                ('model', '=', model[0])
            ])
            menu_id1 = menu_obj.create({
                'name': 'menu1',
                'unique_identifier': 'identifier',
                'website': cls.site1,
                'model': model[0],
                'children_field': children_field[0],
                'uri_field': fields[0],
                'title_field': fields[0],
                'identifier_field': fields[0]
            })
            menu_id2 = menu_obj.create({
                'name': 'menu2',
                'unique_identifier': 'identifier',
                'website': cls.site2,
                'model': model[0],
                'children_field': children_field[0],
                'uri_field': fields[0],
                'title_field': fields[0],
                'identifier_field': fields[0]
            })

            menu1 = menu_obj.browse(menu_id1)
            website1 = website_obj.browse(cls.site1)
            menu2 = menu_obj.browse(menu_id2)
            website2 = website_obj.browse(cls.site2)
            category = prod_categ_obj.browse(category_id)



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

    def setUp(self):
        trytond.tests.test_tryton.install_module('nereid_cms')

        self.currency_obj = POOL.get('currency.currency')
        self.company_obj = POOL.get('company.company')
        self.nereid_user_obj = POOL.get('nereid.user')
        self.url_map_obj = POOL.get('nereid.url_map')
        self.language_obj = POOL.get('ir.lang')
        self.nereid_website_obj = POOL.get('nereid.website')

        self.menu_obj = POOL.get('nereid.cms.menu')

        self.templates = {
            'localhost/home.jinja':
                '{{ menu_for("identifier", "category-name")|safe }}',
        }

    def test_0010_menu_for(self):
        """Two different website, having same unique identifier in
        nereid.cms.menu
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()
            with app.test_client() as c:
                response = c.get('/en_US/')
                rv = literal_eval(response.data)
            self.assertTrue(rv['uri'], 'Category1')


def suite():
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestMenuFor)
        )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
