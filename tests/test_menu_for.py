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
        self.site1 = self.nereid_website_obj.create({
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
        trytond.tests.test_tryton.install_module('product')

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

            ProductCategory = POOL.get('product.category')
            Model = POOL.get('ir.model')
            ModelField = POOL.get('ir.model.field')

            ProductCategory.create({
                'name': 'Category1'
            })
            model = Model.search([
                ('model', '=', 'product.category')
            ])
            fields = ModelField.search([
                ('ttype', '=', 'char'),
                ('model', '=', model[0])
            ])
            children_field = ModelField.search([
                ('ttype', '=', 'one2many'),
                ('model', '=', model[0])
            ])
            self.menu_obj.create({
                'name': 'menu1',
                'unique_identifier': 'identifier',
                'website': self.site1.id,
                'model': model[0].id,
                'children_field': children_field[0].id,
                'uri_field': fields[0].id,
                'title_field': fields[0].id,
                'identifier_field': fields[0].id
            })

            self.templates = {
                'localhost/home.jinja':
                    '{{ menu_for("identifier", "Category1")|safe }}',
            }

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
