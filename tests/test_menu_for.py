#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import unittest2 as unittest
import ast

from trytond.config import CONFIG
CONFIG.options['db_type'] = 'sqlite'
from trytond.modules import register_classes
register_classes()

from nereid.testing import testing_proxy, TestCase
from trytond.transaction import Transaction


class TestMenuFor(TestCase):
    """Test menu_for"""

    @classmethod
    def setUpClass(cls):
        super(TestMenuFor, cls).setUpClass()
        testing_proxy.install_module('nereid_cms')
        testing_proxy.install_module('product')

        menu_obj = testing_proxy.pool.get('nereid.cms.menu')
        website_obj = testing_proxy.pool.get('nereid.website')
        url_obj = testing_proxy.pool.get('nereid.url_map')
        language_obj = testing_proxy.pool.get('ir.lang')
        model_obj = testing_proxy.pool.get('ir.model')
        model_field_obj = testing_proxy.pool.get('ir.model.field')
        prod_categ_obj = testing_proxy.pool.get('product.category')
        article_categ_obj = testing_proxy.pool.get(
            'nereid.cms.article.category'
            )
        article_obj = testing_proxy.pool.get('nereid.cms.article')


        with Transaction().start(testing_proxy.db_name, 1, None) as txn:
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
            home_template = testing_proxy.create_template(
                'home.jinja',
                '{{ menu_for("%s", "%s")|safe }}' % \
                (menu1.unique_identifier, category[0].name),
                cls.site1
            )

            txn.cursor.commit()

    def get_app(self):
        return testing_proxy.make_app(
            SITE='localhost',
        )

    def test_0010_menu_for(self):
        """Two different website, having same unique identifier in 
        nereid.cms.menu
        """
        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/en_US/')
            rv = ast.literal_eval(response.data)
        self.assertTrue(rv['uri'], 'Category1')


def suite():
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestMenuFor)
        )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
