#This file is part of Tryton.  The COPYRIGHT file at the top level
#of this repository contains the full copyright notices and license terms.
"Nereid CMS"

import time
from nereid.templating import render_template
from nereid.threading import local
from nereid.helpers import slugify
from trytond.pyson import Eval
from trytond.model import ModelSQL, ModelView, fields

class CMSMenus(ModelSQL, ModelView):
    "Nereid CMS Menus"
    _name = 'nereid.cms.menus'
    _description = __doc__

    name = fields.Char('Name', size=100, required=True)
    unique_identifier = fields.Char(
        'Unique Identifier', 
        required=True,
        on_change_with=['name', 'unique_identifier']
    )
    description = fields.Text('Description')
    website = fields.Many2One('nereid.website', 'WebSite')
    active = fields.Boolean('Active')

    model = fields.Many2One(
        'ir.model', 
        'Open ERP Model', 
        required=True
    )
    parent_field = fields.Many2One('ir.model.field', 'Parent',
        domain=[
            ('model', '=', Eval('model')),
            ('ttype', '=', 'many2one')
        ], required=True
    )
    children_field = fields.Many2One('ir.model.field', 'Children',
        domain=[
            ('model', '=', Eval('model')),
            ('ttype', '=', 'one2many')
        ], required=True
    )
    uri_field = fields.Many2One('ir.model.field', 'URI Field',
        domain=[
            ('model', '=', Eval('model')),
            ('ttype', '=', 'char')
        ], required=True
    )
    identifier_field = fields.Many2One('ir.model.field', 'Identifier Field',
        domain=[
            ('model', '=', Eval('model')),
            ('ttype', '=', 'char')
        ], required=True
    )

    def default_active(self, cursor, user, context=None):
        """
        By Default the Menu is active
        """
        return True

    def __init__(self):
        super(CMSMenus, self).__init__()
        self._sql_constraints += [
            ('unique_identifier', 'UNIQUE(unique_identifier, website)',
                'The Unique Identifier of the Menu must be unique.'),
        ]

    def _menu_item_to_dict(self, cursor, user, menu_item, menu):
        """
        :param menu_item: BR of the menu item
        :param menu: BR of the menu set
        """
        return {
                'name' : menu_item.name,
                'uri' : getattr(menu_item, menu.uri_field),
            }

    def _generate_menu_tree(self, cursor, user, 
            menu_item_object, menu_item_id, menu, context):
        """
        :param menu_item_object: object from pool
        :param menu_item_id: ID of the remote item
        :param menu: Browse Record of the  menu item
        :param context: Tryton Context
        """
        result = {}
        menu_item = menu_item_object.browse(
            cursor, user, menu_item_id, context)
        result['parent'] = self._menu_item_to_dict(
            cursor, user, menu_item, menu)
        children = getattr(menu_item, menu.children_field.name)
        if children:
            result['children'] = [
                self._menu_item_to_dict(cursor, user, child, menu) \
                    for child in children
                ]
        return result

    def _menu_for(self, cursor, user, identifier,
        ident_field_value, context=None):
        """
        Returns a dictionary of menu tree

        :param cursor: Database Cursor
        :param user: ID of the user
        :param identifier: The unique identifier from which the menu
                has to be chosen
        :param ident_field_value: The value of the field that has to be 
                looked up on model with search on ident_field
        :param context: Tryton context
        """
        # First pick up the menu through identifier
        menu_id = self.search(cursor, user, [
            ('unique_identifier', '=', identifier)
            ], limit=1, context=context)
        if not menu_id:
            # TODO: May be raise an error ? Look at some other app
            # how this is handled
            return None
        menu_id = menu_id[0]
        menu = self.browse(cursor, user, menu_id, context)

        # Get the data from the model
        menu_item_object = self.pool.get(menu.model.model)
        menu_item_id = menu_item_object.search(cursor, user, 
            [(menu.identifier_field.name, '=', ident_field_value)],
            limit=1, context=context
            )
        if not menu_item_id:
            # Raise error ?
            return None
        return self._generate_menu_tree(cursor, user, 
            menu_item_object, menu_item_id, menu, context)

    def menu_for(self, request):
        """
        Template context processor method

        This method could be used to fetch a specific menu for like
        a wrapper from the templates

        From the templates the usage would be:

        `menu_for('category_menu', 'all_products')`
        """
        def wrapper(identifier, ident_field_value):
            return self._menu_for(
                local.transaction.cursor,
                request.tryton_user.id,
                identifier, ident_field_value,
                request.tryton_context
            )
        return {'menu_for': wrapper}

    def on_change_with_unique_identifier(self, cursor, 
                                        user, vals, context=None):
        if vals.get('name'):
            if not vals.get('unique_identifier'):
                vals['unique_identifier'] = slugify(vals['name'])
            return vals['unique_identifier']

CMSMenus()


class CMSMenuitems(ModelSQL, ModelView):
    "Nereid CMS Menuitems"
    _name = 'nereid.cms.menuitems'
    _description = __doc__
    _rec_name = 'unique_name'
    _order = 'sequence'
    
    title= fields.Char('Title', size=100, required=True,)
    unique_name= fields.Char(
        'Unique Name', 
        size=100, required=True, 
        on_change_with=['title', 'unique_name'])
    link= fields.Char('Link', size=255,)
    parent= fields.Many2One('nereid.cms.menuitems', 'Parent Menuitem',)
    child_id= fields.One2Many(
        'nereid.cms.menuitems', 
        'parent', 
        string='Child Menu Items'
    )
    active= fields.Boolean('Active')
    sequence= fields.Integer('Sequence', required=True,)

    def default_active(self, cursor, user, context=None ):
        return True

    def check_recursion(self, cursor, user, ids):
        """
        Check the recursion beyond a certain limit.
      
        :param cursor: Database Cursor
        :param user: ID of User
        :param ids: ID of Current Record

        : return: True
        """
        level = 100
        while len(ids):
            cursor.execute('select distinct parent from nereid_cms_menuitems \
                                        where id in (' + ','.join(
                                                        map(str, ids)
                                                        ) + ')')
            ids = filter(None, map(lambda x:x[0], cursor.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    def __init__(self):
        super(CMSMenuitems, self).__init__()
        self._constraints += [
            ('check_recursion', 'wrong_recursion')
        ]
        self._error_messages.update({
            'wrong_recursion': 
            'Error ! You can not create recursive menuitems.',
        })
    
    def on_change_with_unique_name(self, cursor, 
                                        user, vals, context=None):
        if vals.get('title'):
            if not vals.get('unique_name'):
                vals['unique_name'] = slugify(vals['title'])
            return vals['unique_name']

CMSMenuitems()


class ArticleCategory(ModelSQL, ModelView):
    "Article Categories"
    _name = 'nereid.article.category'
    _description = __doc__
    _rec_name = 'unique_name'

    title = fields.Char('Title', size=100, required=True,)
    unique_name = fields.Char(
        'Unique Name', 
        required=True,
        on_change_with=['title', 'unique_name'],
    )
    active= fields.Boolean('Active',)
    description= fields.Text('Description',)

    def default_active(self, cursor, user, context=None ):
        'Return True' 
        return True
    
    def __init__(self):
        super(ArticleCategory, self).__init__()
        self._sql_constraints += [
            ('unique_name', 'UNIQUE(unique_name)',
                'The Unique Name of the Category must be unique.'),
        ]
    
    def on_change_with_unique_name(self, cursor, 
                                        user, vals, context=None):
        if vals.get('title'):
            if not vals.get('unique_name'):
                vals['unique_name'] = slugify(vals['title'])
            return vals['unique_name']

ArticleCategory()


class CMSArticles(ModelSQL, ModelView):
    "CMS Articles"
    _name = 'nereid.cms.article'
    _inherits = {'nereid.flatpage': 'flatpage_id'}
    _order = 'sequence'
    
    flatpage_id = fields.Many2One(
        'nereid.flatpage',
        'Flatpage', 
        required=True
    )
    active = fields.Boolean('Active')
    category = fields.Many2One(
        'nereid.article.category', 
        'Category',
        required=True,
    )
#    image= fields.Many2One('nereid.static.file', 'Image',)
    author = fields.Many2One('res.user', 'Author',)
    create_date = fields.DateTime('Created Date')
    published_on = fields.DateTime('Published On')
    sequence= fields.Integer('Sequence', required=True,)
    # TODO: Meta Information

    def default_active(self, cursor, user, context=None ):
        return True
    
    def default_author(self, cursor, user, context=None ):
        return user
    
    def default_create_date(self, cursor, user, context=None ):
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def default_published_on(self, cursor, user, context=None ):
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def render(self, cursor, request, arguments=None):
        """
        Renders the template
        """
        uri = arguments.get('uri', None)
        if uri:
            article_ids = self.search(cursor, request.tryton_user.id, 
                                       [
                                        ('uri', '=', uri)
                                        ], 
                                        context = request.tryton_context)
            if article_ids:
                article = self.browse(cursor, request.tryton_user.id, 
                                       article_ids[0], 
                                       context = request.tryton_context)
                template_name = article.template.name
                html = render_template(template_name, article=article)            
                return local.application.response_class(html, 
                                                        mimetype='text/html')
        
CMSArticles()
