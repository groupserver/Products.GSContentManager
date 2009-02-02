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

class ManagePagesForm(PageForm):
    label = u'Manage Pages'
    pageTemplateFileName = 'browser/templates/manage_pages.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSMangePages,
        render_context=False, omit_readonly=False)

    implements(IGSContentPageVersion)
    
    def __init__(self, folder, request):
        PageForm.__init__(self, folder, request)
        self.folder = folder
        self.siteInfo = createObject('groupserver.SiteInfo', folder)
        
        self.auditor = None
    
    @form.action(label=u'Add', failure='action_failure')
    def handle_add(self, action, data):
        '''Change the data that is being 
        '''
        pass
        return retval

    @form.action(label=u'Copy', failure='action_failure')
    def handle_copy(self, action, data):
        '''Change the data that is being 
        '''
        pass
        return retval

    @form.action(label=u'Rename', failure='action_failure')
    def handle_rename(self, action, data):
        '''Change the data that is being 
        '''
        pass
        return retval

    @form.action(label=u'Move', failure='action_failure')
    def handle_move(self, action, data):
        '''Change the data that is being 
        '''
        pass
        return retval

    def action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

