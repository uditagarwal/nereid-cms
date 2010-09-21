#This file is part of Tryton.  The COPYRIGHT file at the top level
#of this repository contains the full copyright notices and license terms.
"Nereid CMS"

import time
from trytond.model import ModelSQL, ModelView, fields

class CMSMenus(ModelSQL, ModelView):
    "Nereid CMS Menus"
    _name = 'nereid.cms.menus'
    _description = __doc__

    name= fields.Char('Name', size=100, required=True)
    unique_identifier = fields.Char(
        'Unique Identifier', 
        size=100, required=True,)
    description= fields.Text('Description')
    site= fields.Many2One('nereid.sites', 'Site')
    active= fields.Boolean('Active')
    
    model=fields.Many2One('ir.model', 'Open ERP Model', required=True,)
    parent_field = fields.Many2One('ir.model.field', 'Parent',
        domain=[
            ('model', '=', Eval('model'))
            ('ttype', '=', 'many2one')
        ], required=True
    )
    children_field = fields.Many2One('ir.model.field', 'Children',
        domain=[
            ('model', '=', Eval('model'))
            ('ttype', '=', 'one2many')
        ], required=True
    )
    uri_field = fields.Many2One('ir.model.field', 'URI Field',
        domain=[
            ('model', '=', Eval('model'))
            ('ttype', '=', 'char')
        ], required=True
    )
    identifier_field = fields.Many2One('ir.model.field', 'Identifier Field',
        domain=[
            ('model', '=', Eval('model'))
            ('ttype', '=', 'char')
        ], required=True
    )

    def default_active(self, cursor, user, context=None ):
        return True

    _sql_constraints = [
        ('unique_identifier', 'unique(unique_identifier, site)',
                    'The Unique Identifier of the Menu must be unique.')
    ]

CMSMenus()


class CMSMenuitems(ModelSQL, ModelView):
    "Nereid CMS Menuitems"
    _name = 'nereid.cms.menuitems'
    _description = __doc__
    _rec_name = 'unique_name'
    _order = 'sequence'
    
    title= fields.Char('Title', size=100, required=True,)
    unique_name= fields.Char('Unique Name', size=100, required=True)
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
            cursor.execute('select distinct parent from cms_menuitems where \
                                        id in (' + ','.join(
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

CMSMenuitems()


class ArticleCategory(ModelSQL, ModelView):
    "Article Categories"
    _name = 'nereid.article.category'
    _description = __doc__
    _rec_name = 'unique_name'

    title = fields.Char('Title', size=100, required=True,)
    unique_name = fields.Char('Unique Name', size=100, required=True,)
    active= fields.Boolean('Active',)
    description= fields.Text('Description',)

    def defaults_active(self, cursor, user, context=None ):
        'Return True' 
        return True

    _sql_constraints = [
        ('unique_name', 'unique(unique_name)',
                    'The Unique Name of the Category must be unique.')
    ]

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
    active= fields.Boolean('Active')
    category= fields.Many2One(
        'nereid.article.category', 
        'Category',
        required=True,
    )
    image= fields.Many2One('nereid.static.file', 'Image',)
    author= fields.Many2One('res.users', 'Author',)
    create_date = fields.DateTime('Created Date')
    published_on= fields.DateTime('Published On')
    sequence= fields.Integer('Sequence', required=True,)
    # TODO: Mets Information

    def default_active(self, cursor, user, context=None ):
        return True
    
    def default_author(self, cursor, user, context=None ):
        return user
    
    def default_create_date(self, cursor, user, context=None ):
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def default_published_on(self, cursor, user, context=None ):
        return time.strftime("%Y-%m-%d %H:%M:%S")
        
CMSArticles()