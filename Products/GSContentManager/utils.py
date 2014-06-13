# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 E-Democracy.org and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from datetime import datetime
import pytz
from gs.core import comma_comma_and, to_ascii
from .interfaces import IGSContentPageVersion
CONTENT_TEMPLATE = 'content_en'


def new_version(folder, newId):
    '''Create a new (blank) version of a document'''
    manageAdd = folder.manage_addProduct['PageTemplates']
    # --=mpj17=-- If the text is not set, the page template will
    #   try and acquire the text from its parent when the form
    #   tries to set the text. (I know, do not get me started.)
    #   By setting the text here we stop the madness.
    manageAdd.manage_addPageTemplate(to_ascii(newId), title='',
      text='GSNotSet', REQUEST=None)
    template = getattr(folder, newId)
    assert template.getId() == newId
    assert template.meta_type == 'Page Template'
    retval = IGSContentPageVersion(template)
    assert retval
    return retval


def new_version_id():
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    t = now.strftime("%Y%m%d%H%M%S")
    retval = to_ascii('%s_%s' % (CONTENT_TEMPLATE, t))
    assert retval
    return retval


roleMap = {
  'Anonymous': 'anyone',
  'Authenticated': 'people who are logged in',
  'DivisionMember': 'members of this site',
  'GroupMember': 'members of this group',
  'admins': 'the site administrators',
  'Manager': 'the system administrators',
}


def rolesToDescriptions(roles):
    k = list(roleMap.keys())
    rs = [r.strip() for r in roles if (r.strip() in k)]
    if len(rs) > 1:
        try:
            rs.remove('Manager')
        except ValueError:
            pass

    if (('GroupAdmin' in roles) or ('DivisionAdmin' in roles)):
        rs.append('admins')

    ds = [r for r in [roleMap.get(r, '') for r in rs] if r]
    retval = comma_comma_and(ds)
    return retval
