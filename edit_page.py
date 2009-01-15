# coding=utf-8
'''Implementation of the Edit Page form.
'''
from time import strftime, gmtime, time
import difflib, pytz
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
from interfaces import *
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
    form_fields = form.Fields(IGSContentPageVersion,
        render_context=True, omit_readonly=False)

    implements(IGSContentPageVersion)
    
    def __init__(self, folder, request):
        PageForm.__init__(self, folder, request)
        self.form_fields['content'].custom_widget = wym_editor_widget
        
        self.folder = folder
        self.siteInfo = createObject('groupserver.SiteInfo', folder)
        
        # Get the version of the page for editing; default to HEAD
        hist = GSPageHistory(folder)
        ev = request.form.get('form.edited_version', hist.current.id)
        assert ev in hist, u'%s not in %s' % (ev, hist.keys())
        self.versionForChange = hist[ev]
        
        self.auditor = None
    
    def setUpWidgets(self, ignore_request=False):
        # There is a litle voodoo here. A PageForm normally wraps 
        #   the instance that holds the data. In this case we want
        #   the data to come from the version that is being 
        #   edited. To do this we pass "versionForChange" to the
        #   widgets.
        self.adapters = {}
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.versionForChange,
            self.request, form=self, adapters=self.adapters,
            ignore_request=ignore_request)
    
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
        return self.set_data(data)

    def set_data(self, data):
        assert self.folder
        assert self.form_fields
        assert self.versionForChange
        assert self.auditor
        assert data

        newVersion = self.new_version()
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

    def new_version(self):
        '''Create a new (blank) version of the document'''
        newId = self.new_version_id()
        manageAdd = self.folder.manage_addProduct['DataTemplates']
        manageAdd.manage_addXMLTemplate(newId, None)
        xmlDataTemplate = getattr(self.folder, newId)
        assert xmlDataTemplate.getId() == newId
        assert xmlDataTemplate.meta_type == 'XML Template'
        retval = IGSContentPageVersion(xmlDataTemplate)
        assert retval
        return retval

    def new_version_id(self):
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        t = now.strftime("%Y%m%d%H%M%S")
        retval = '%s_%s' % (CONTENT_TEMPLATE, t)
        assert type(retval) == str
        assert not(hasattr(self.folder, retval))
        assert retval
        return retval

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
        
        ovt = oldVer.content.split('\n')
        nvt = newVer.content.split('\n')
        d = difflib.unified_diff(ovt, nvt, oldVer.id, newVer.id)
        retval = u'\n'.join(d)
        assert type(retval) == unicode
        return retval

    def get_html_diff(self, oldVer, newVer):
        assert oldVer 
        assert newVer 
        
        ovt = oldVer.content.split('\n')
        ovDesc = self.get_version_description(oldVer)
        nvt = newVer.content.split('\n')
        nvDesc = self.get_version_description(newVer)

        htmlDiffer = difflib.HtmlDiff(tabsize=2)
        retval = htmlDiffer.make_table(ovt, nvt, ovDesc, nvDesc)
        
        assert retval
        return retval

    def get_version_description(self, ver):
        vUI = createObject('groupserver.UserFromId', 
                            self.folder, ver.editor)
        dt = munge_date(self.folder, 
          ver.creationDate, '%Y %b %d %H:%M:%S')
        retval = u'%s (%s)' % (userInfo_to_anchor(vUI),dt)
        assert retval
        assert type(retval) == unicode
        return retval 

