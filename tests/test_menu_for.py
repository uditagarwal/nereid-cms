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
        self.templates = {
            'localhost/home.jinja':
                '{{ menu_for("identifier", "Category1")|safe }}',
        }
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
        self.site = self.nereid_website_obj.create({
            'name': 'localhost',
            'url_map': url_map_id,
            'company': company_id,
            'application_user': USER,
            'default_language': en_us,
            'guest_user': guest_user,
            'currencies': [('set', [usd])],
        })

    def setUp(self):
        trytond.tests.test_tryton.install_module('product')
        trytond.tests.test_tryton.install_module('nereid_cms')

        self.currency_obj = POOL.get('currency.currency')
        self.company_obj = POOL.get('company.company')
        self.nereid_user_obj = POOL.get('nereid.user')
        self.url_map_obj = POOL.get('nereid.url_map')
        self.language_obj = POOL.get('ir.lang')
        self.nereid_website_obj = POOL.get('nereid.website')
        self.menu_obj = POOL.get('nereid.cms.menu')

    def test_0010_menu_for(self):
        """Two different website, having same unique identifier in
        nereid.cms.menu
        """
        menu_obj = POOL.get('nereid.cms.menu')
        model_obj = POOL.get('ir.model')
        model_field_obj = POOL.get('ir.model.field')
        prod_categ_obj = POOL.get('product.category')

        with Transaction().start(DB_NAME, USER, CONTEXT):

            self.setup_defaults()

            prod_categ_obj.create({'name': 'Category1'})
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
            menu_obj.create({
                'name': 'menu1',
                'unique_identifier': 'identifier',
                'website': self.site,
                'model': model[0],
                'children_field': children_field[0],
                'uri_field': fields[0],
                'title_field': fields[0],
                'identifier_field': fields[0]
            })
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
