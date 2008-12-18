# coding=utf-8
'''Implementation of the Edit Page form.
'''
from time import strftime, gmtime, time
import difflib
from datetime import datetime
from base64 import b64encode
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject, adapts
from zope.interface import implements, providedBy, implementedBy,\
  directlyProvidedBy, alsoProvides
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import MultiCheckBoxWidget, SelectWidget,\
  TextAreaWidget
from zope.security.interfaces import Forbidden
from zope.app.apidoc.interface import getFieldsInOrder
from zope.schema import *
from Products.XWFCore.XWFUtils import comma_comma_and, munge_date
from interfaces import IGSContentPage, IGSEditContentPage
from page import GSContentPage
from audit import PageEditAuditor, EDIT_CONTENT
from page_history import GSPageHistory
from Products.GSProfile.utils import enforce_schema
from Products.CustomUserFolder.userinfo import userInfo_to_anchor

import logging
log = logging.getLogger('GSContentManager')

CONTENT_TEMPLATE = 'content_en'

def wym_editor_widget(field, request):
    retval = TextAreaWidget(field, request)
    retval.cssClass = 'wymeditor'
    return retval

class EditPageForm(PageForm):
    label = u'Edit Page'
    pageTemplateFileName = 'browser/templates/edit_page.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        # Adapt the context object to a content page object
        self.folder = context
        self.hist = hist = GSPageHistory(context)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.interface = IGSEditContentPage

        self.ev = ev = request.form.get('form.edited_version', 
            hist.current.getId())
        assert ev in hist, u'%s not in %s' % (ev, hist.keys())
        request.form['form.content'] = hist[ev]()

        self.form_fields = form.Fields(self.interface, 
            render_context=True, omit_readonly=True)
        self.form_fields['content'].custom_widget = wym_editor_widget
        
        self.auditor = None
        
    @property
    def id(self):
        return self.folder.getId()

    @property
    def title(self):
        return self.hist[self.ev].title_or_id()
    
    @property
    def description(self):
        return ''
        # self.content_page.description

    @property
    def content(self):
        c = self.hist[self.ev]()
        return c

    def action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    #@form.action(label=u'Publish', failure='action_failure')
    def handle_publish(self, action, data):
        # --=mpj17=-- This needs a complete rewrite, and I need to
        #   figure out how to attach it to the form.
        copied_revision = False and self.request.get('copied_revision', None)
        published_revision = False and    self.request.get('published_revision', 
          None)

        if published_revision:
            # Handle publishing of a selected revision.
            # --=mpj17=-- replace
            # self.content_page.publish_revision(published_revision)
            self.status = u'Revision %s has been made the '\
              u'published revision.' % published_revision
        elif copied_revision:
            # Handle copying of a selected revision to current
            # --=mpj17=-- replace
            # self.content_page.copy_revision_to_current(copied_revision)
            self.status = u'Revision %s has been copied to current '\
              u'for editing.' % copied_revision
    
    @form.action(label=u'Change', failure='action_failure')
    def handle_set(self, action, data):
        '''Change the data that is being 
        '''
        self.auditor = PageEditAuditor(self.context)
        return self.set_data(data)

    def set_data(self, data):
        assert self.folder
        assert self.form_fields
        userInfo = createObject('groupserver.LoggedInUser',self.context)
        
        # Save the new version in the history
        newVersion = self.new_version()
        newVersion.write(data['content'])
        newVersion.title = data['title']
        newVersion.manage_addProperty('editor', userInfo.id, 'ustring')
        self.auditor.info(EDIT_CONTENT)
        self.status = u'Changed %s' % data['title']
        assert self.status
        assert type(self.status) == unicode

    def new_version(self):
        '''Create a new (blank) version of the document'''
        newId = self.new_version_id()
        manageAdd = self.folder.manage_addProduct['DataTemplates']
        manageAdd.manage_addXMLTemplate(newId, None)
        retval = getattr(self.folder, newId)
        assert retval
        assert retval.meta_type == 'XML Template'
        return retval

    def new_version_id(self):
        t = strftime("%Y%m%d%H%M%S", gmtime(time()))
        retval = '%s_%s' % (CONTENT_TEMPLATE, t)
        assert type(retval) == str
        assert retval
        return retval

    def get_changed(self, oldContent, newContent, skip = []):
        fields = [field for field in getFieldsInOrder(self.interface)
                  if not field[1].readonly]
        alteredFields = []
        for field in fields:
            fieldId = field[0]
            if fieldId not in skip:
                new = getattr(newContent, fieldId, '')
                old = getattr(oldContent, fieldId, '')
                if (old != new):
                    alteredFields.append(fieldId)
        assert type(alteredFields) == list
        return alteredFields

    def get_auditDatums(self, oldVer, newVer):
        url = self.folder.absolute_url(0)
        title = oldVer.title_or_id()
        instanceDatum = u','.join((b64encode(url), b64encode(title),
            oldVer.getId(), newVer.getId()))

        textDiff = self.get_text_diff(oldVer, newVer)
        htmlDiff = self.get_html_diff(oldVer, newVer)
        supplementaryDatum = u','.join((b64encode(textDiff),
                                        b64encode(htmlDiff)))
        retval = (instanceDatum, supplementartDatum)
        assert len(retval) == 2
        assert type(retval[0]) == unicode
        assert type(retval[1]) == unicode
        return retval

    def get_text_diff(self, oldVer, newVer):
        assert oldVer 
        assert oldVer.meta_type == 'XML Template'
        assert newVer 
        assert newVer.meta_type == 'XML Template'
        
        ovt = oldVer().split('\n')
        ovDesc = oldVer.getId()
        nvt = newVer().split('\n')
        nvDesc = newVer.getId()
        d = difflib.unified_diff(ovt, nvt, ovDesc, nvDesc)
        retval = u'\n'.join(d)
        assert type(retval) == unicode
        assert retval
        return retval

    def get_html_diff(self, oldVer, newVer):
        assert oldVer 
        assert oldVer.meta_type == 'XML Template'
        assert newVer 
        assert newVer.meta_type == 'XML Template'
        
        ovt = oldVer().split('\n')
        ovDesc = self.get_version_description(oldVer)
        nvt = newVer().split('\n')
        nvDesc = self.get_version_description(newVer)

        htmlDiffer = difflib.HtmlDiff(tabsize=2)
        retval = htmlDiffer.make_table(ovt, nvt, ovDesc, nvDesc)
        
        assert retval
        return retval

    def get_version_description(self, ver):
        vTimeStamp = float(ver.getId().split('_')[-1])
        vDate = datetime.fromtimestamp(vTimeStamp)
        vUI = createObject('groupserver.UserFromId', 
                            self.folder, ver.editor)
        retval = u'%s (%s)' % (userInfo_to_anchor(vUI),
                               munge_date(vDate,'%Y %b %d %H:%M:%S'))
        assert retval
        assert type(retval) == unicode
        return retval 

