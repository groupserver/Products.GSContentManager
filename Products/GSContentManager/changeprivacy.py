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
from AccessControl.PermissionRole import rolesForPermissionOn
from zope.interface import implementer
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.content.form.base import (radio_widget, SiteForm)
from .interfaces import IGSChangePagePrivacy
from .utils import rolesToDescriptions
from .page_history import GSPageHistory


@implementer(IGSChangePagePrivacy)
class ChangePrivacyForm(SiteForm):
    label = 'Change Privacy'
    pageTemplateFileName = 'browser/templates/change_privacy.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSChangePagePrivacy,
        render_context=False, omit_readonly=False)

    def __init__(self, folder, request):
        super(ChangePrivacyForm, self).__init__(folder, request)
        self.folder = folder
        self.hist = GSPageHistory(folder)
        self.perms = Permissions(folder)

        self.form_fields['view'].custom_widget = radio_widget
        self.form_fields['change'].custom_widget = radio_widget

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        data = {
          'view': self.perms.view,
          'change': self.perms.change,
        }
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.folder,
            self.request, form=self, data=data,
            ignore_request=ignore_request)

    @form.action(label='Change', failure='action_failure')
    def handle_change(self, action, data):
        self.status = ''
        if self.perms.view != data['view']:
            self.perms.view = data['view']
            # --=mpj17=-- TODO: make better
            self.status = 'Altered who can view the page.'
        if self.perms.change != data['change']:
            self.perms.change = data['change']
            # --=mpj17=-- TODO: make better
            self.status = '%s Altered who can change the page.' %\
              self.status
        # assert self.status

    def action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = '<p>There is an error:</p>'
        else:
            self.status = '<p>There are errors:</p>'

    @property
    def title(self):
        return self.hist.published.title

    @property
    def changePermissionRoles(self):
        retval = rolesForPermissionOn('Change permissions', self.context)
        assert type(retval) in (tuple, list),\
          'retval is a %s, not a tuple or list: %s' % (type(retval), retval)
        return retval

    @property
    def changePermissionRolesDescription(self):
        return rolesToDescriptions(self.changePermissionRoles)


class Permissions(object):
    roleMap = {
      'Anonymous': 'anyone',
      'DivisionMember': 'members',
      'GroupMember': 'members',
      'DivisionAdmin': 'administrators',
      'GroupAdmin': 'administrators',
      'Manager': 'administrators',
    }
    anyone = ('Anonymous', 'Authenticated',
      'DivisionMember', 'DivisionAdmin',
      'GroupMember', 'GroupAdmin', 'Manager')
    members = ('DivisionMember', 'DivisionAdmin',
      'GroupMember', 'GroupAdmin', 'Manager')
    administrators = ('DivisionAdmin', 'GroupAdmin', 'Manager')

    reverseRoleMap = {
      'anyone': anyone,
      'members': members,
      'administrators': administrators,
    }

    def __init__(self, page):
        self.page = page

    def get_view(self):
        roles = rolesForPermissionOn('View', self.page)
        retval = self.reduce_roles(roles)
        return retval

    def reduce_roles(self, roles):
        k = list(self.roleMap.keys())
        mapedRoles = set([self.roleMap[r] for r in roles if r in k])
        if ('anyone' in mapedRoles):
            retval = 'anyone'
        elif ('members' in mapedRoles):
            retval = 'members'
        elif ('administrators' in mapedRoles):
            retval = 'administrators'
        else:
            retval = 'other'
        return retval

    def set_view(self, v):
        assert v in list(self.reverseRoleMap.keys())
        roles = self.reverseRoleMap[v]
        self.page.manage_permission('View', roles)

    view = property(get_view, set_view)

    def get_change(self):
        roles = rolesForPermissionOn('Manage properties', self.page)
        retval = self.reduce_roles(roles)
        return retval

    def set_change(self, v):
        assert v in list(self.reverseRoleMap.keys())
        roles = self.reverseRoleMap[v]
        self.page.manage_permission('Manage properties', roles)
        self.page.manage_permission('View History', roles)  # --=Split=--

    change = property(get_change, set_change)
