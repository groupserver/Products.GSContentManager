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
from __future__ import absolute_import
import difflib
from base64 import b64encode
from zope.app.form.browser import TextAreaWidget
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore.XWFUtils import munge_date
from gs.content.form.base import SiteForm
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from .audit import PageEditAuditor, EDIT_CONTENT
from .interfaces import IGSContentPageVersion
from .page_history import GSPageHistory
from .utils import new_version, new_version_id

import logging
log = logging.getLogger('GSContentManager')


def wym_editor_widget(field, request):
    retval = TextAreaWidget(field, request)
    retval.cssClass = 'wymeditor'
    return retval


class EditPageForm(SiteForm):
    label = u'Edit Page'
    pageTemplateFileName = 'browser/templates/edit_page.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, folder, request):
        super(EditPageForm, self).__init__(folder, request)
        self.folder = folder
        self.auditor = None

    @Lazy
    def form_fields(self):
        retval = form.Fields(IGSContentPageVersion, render_context=True,
                                omit_readonly=False)
        retval['content'].custom_widget = wym_editor_widget
        return retval

    @Lazy
    def hist(self):
        retval = GSPageHistory(self.folder)
        return retval

    @Lazy
    def versionForChange(self):
        # Get the version of the page for editing; default to HEAD
        ev = self.request.form.get('form.edited_version', self.hist.current.id)
        assert ev in self.hist, u'%s not in %s' % (ev, self.hist.keys())
        retval = self.hist[ev]
        return retval

    def setUpWidgets(self, ignore_request=False):
        # There is a litle voodoo here. A PageForm normally wraps
        #   the instance that holds the data. In this case we want
        #   the data to come from the version that is being
        #   edited. To do this we pass "versionForChange" to the
        #   widgets.
        self.adapters = {}
        data = {
          'id': self.versionForChange.id,
          'title': self.versionForChange.title,
          'published': self.defaultPublishedOption,  # --=mpj17=--
          'editor': self.versionForChange.editor,
          'creationDate': self.versionForChange.creationDate,
        }
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.versionForChange,
            self.request, form=self, data=data,
            ignore_request=ignore_request)

    @property
    def defaultPublishedOption(self):
        # The published option should be
        #  * OFF if the currently version is off
        #  * OFF if the edited version is not the published version
        #  * ON if the edited version is ON
        retval = ((self.hist.current.published and
            (self.hist.current.id == self.versionForChange.id))
            or
            (self.hist.published.id == self.versionForChange.id))
        assert type(retval) == bool
        return retval

    @property
    def earliestVersionInHistory(self):
        vfcCd = self.versionForChange.creationDate
        pCd = self.hist.published.creationDate
        if vfcCd < pCd:
            retval = self.versionForChange.id
        else:
            retval = self.hist.published.id

        assert retval
        assert retval in self.hist
        return retval

    @property
    def id(self):
        return self.folder.getId()

    @property
    def title(self):
        return self.versionForChange.title

    def action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    @form.action(label=u'Change', failure='action_failure')
    def handle_set(self, action, data):
        '''Change the data that is being
        '''
        self.auditor = PageEditAuditor(self.context)
        retval = self.set_data(data)
        self.versionForChange = self.hist[self.hist.current.id]
        return retval

    def set_data(self, data):
        assert self.folder
        assert self.form_fields
        assert self.versionForChange
        assert self.auditor
        assert data

        nvId = new_version_id()
        while nvId in self.folder.objectIds():
            nvId = new_version_id()
        newVersion = new_version(self.folder, nvId)
        fields = self.form_fields.omit('id', 'parentVersion',
          'editor', 'creationDate')
        form.applyChanges(newVersion, fields, data)
        newVersion.parentVersion = self.versionForChange.id
        userInfo = createObject('groupserver.LoggedInUser',
          self.folder)
        newVersion.editor = userInfo.id

        i, s = self.get_auditDatums(self.versionForChange,
          newVersion)
        self.auditor.info(EDIT_CONTENT, i, s)

        # Handle publishing here
        if data['published']:
            self.folder.published_revision = newVersion.id
        self.status = u'%s %s' % \
          (data['published'] and 'Published' or 'Changed',
           data['title'])
        assert self.status
        assert type(self.status) == unicode

    def get_auditDatums(self, oldVer, newVer):
        url = self.folder.absolute_url(0)
        instanceDatum = u','.join((b64encode(url),
            b64encode(oldVer.title), b64encode(oldVer.id),
            b64encode(newVer.title), b64encode(newVer.id)))

        textDiff = self.get_text_diff(oldVer, newVer)
        htmlDiff = self.get_html_diff(oldVer, newVer)
        supplementaryDatum = u','.join((b64encode(textDiff),
                                        b64encode(htmlDiff)))
        retval = (instanceDatum, supplementaryDatum)
        assert len(retval) == 2
        assert type(retval[0]) == unicode
        assert type(retval[1]) == unicode
        return retval

    def get_text_diff(self, oldVer, newVer):
        assert oldVer
        assert newVer
        # Note we have to convert the text to Unicode, from UTF-8
        ovt = oldVer.content.decode('utf-8').split('\n')
        nvt = newVer.content.decode('utf-8').split('\n')
        d = difflib.unified_diff(ovt, nvt, oldVer.id, newVer.id)
        retval = u'\n'.join(d).encode('utf-8')
        # And convert it back to utf-8, so we can Base64 encode it.
        assert type(retval) == str
        return retval

    def get_html_diff(self, oldVer, newVer):
        # --=mpj17=--
        # The sequence of characters from the browser is in UTF-8.
        #   (If it is not I will leap from this hell-hole of
        #   electronics and punch you on the nose.) This has to be
        #   decoded from UTF-8 (a sequence of bytes) into a Unicode
        #   string (a great and wondrous thing). This string must
        #   then be encoded into ASCII (a sequence of bytes), but
        #   this time replacing the weird characters with XML
        #   character entities.
        assert oldVer
        assert newVer

        ovt = [t.encode('ascii', 'xmlcharrefreplace')
               for t in oldVer.content.decode('utf-8').split('\n')]
        d = self.get_version_description(oldVer)
        ovDesc = d.encode('ascii', 'xmlcharrefreplace')

        nvt = [t.encode('ascii', 'xmlcharrefreplace')
               for t in newVer.content.decode('utf-8').split('\n')]
        d = self.get_version_description(newVer)
        nvDesc = d.encode('ascii', 'xmlcharrefreplace')

        htmlDiffer = difflib.HtmlDiff(tabsize=2)
        retval = htmlDiffer.make_table(ovt, nvt, ovDesc, nvDesc)

        assert retval
        return retval

    def get_version_description(self, ver):
        vUI = createObject('groupserver.UserFromId',
                            self.folder, ver.editor)
        dt = munge_date(self.folder,
          ver.creationDate, '%Y %b %d %H:%M:%S')
        if vUI.anonymous:
            retval = u'an %s (%s)' % (vUI.name.lower(), dt)
        else:
            retval = u'%s (%s)' % (userInfo_to_anchor(vUI), dt)
        assert retval
        assert type(retval) == unicode
        return retval
