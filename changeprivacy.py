# coding=utf-8
'''Implementation of the Page Privacy form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject, adapts
from zope.component.interfaces import IFactory
from zope.interface import implements, providedBy, implementedBy,\
  directlyProvidedBy, alsoProvides
from zope.formlib import form
from zope.copypastemove import ItemNotFoundError
from zope.exceptions import DuplicationError
from zope.app.container.interfaces import IContainer, IOrderedContainer
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import MultiCheckBoxWidget, SelectWidget,\
  TextAreaWidget
from zope.app.apidoc.interface import getFieldsInOrder
from zope.schema import *
from Products.XWFCore.XWFUtils import comma_comma_and, \
  add_marker_interfaces
from interfaces import *
from utils import *
from pagetree import *

class ChangePivacyForm(PageForm):
    label = u'Change Privacy'
    pageTemplateFileName = 'browser/templates/change_privacy.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSP,
        render_context=False, omit_readonly=False)

    implements(IGSChangePagePrivacy)
    
    def __init__(self, folder, request):
        PageForm.__init__(self, folder, request)
        self.folder = folder
        self.siteInfo = createObject('groupserver.SiteInfo', folder)

    @form.action(label=u'Change', failure='action_failure')
    def handle_change(self, action, data):
        self.status = u'I cannot handle change!'
        assert self.status
        assert type(self.status) == unicode
        
    def action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

