# -*- coding: utf-8 -*-
'''

    nereid_cms

    :copyright: (c) 2010-2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''

from trytond.pool import Pool
from .cms import *


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
        module='nereid_cms', type_='model')
