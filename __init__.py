# -*- coding: utf-8 -*-
'''

    nereid_cms

    :copyright: (c) 2010-2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''

from trytond.pool import Pool
from .cms import (
    CMSLink, Menu, MenuItem, BannerCategory, Banner, ArticleCategory,
    Article, ArticleAttribute
)


def register():
    """
    Register classes
    """
    Pool.register(
        CMSLink,
        Menu,
        MenuItem,
        BannerCategory,
        Banner,
        ArticleCategory,
        Article,
        ArticleAttribute,
        module='nereid_cms', type_='model'
    )
