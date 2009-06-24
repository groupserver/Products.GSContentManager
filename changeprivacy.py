# coding=utf-8
'''Implementation of the Page Privacy form.
'''
from AccessControl.PermissionRole import rolesForPermissionOn
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject, adapts
from zope.interface import implements, providedBy, implementedBy
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore.XWFUtils import comma_comma_and
from Products.GSGroup.changebasicprivacy import radio_widget
from interfaces import *
from utils import *
from page_history import GSPageHistory

class ChangePrivacyForm(PageForm):
    label = u'Change Privacy'
    pageTemplateFileName = 'browser/templates/change_privacy.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSChangePagePrivacy,
        render_context=False, omit_readonly=False)

    implements(IGSChangePagePrivacy)
    
    def __init__(self, folder, request):
        PageForm.__init__(self, folder, request)
        self.folder = folder
        self.siteInfo = createObject('groupserver.SiteInfo', folder)
        self.hist = GSPageHistory(folder)
        self.form_fields['view'].custom_widget = radio_widget
        self.form_fields['change'].custom_widget = radio_widget

    @property
    def title(self):
        return self.hist.published.title
    
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

    @property
    def changePermissionRoles(self):
        retval = rolesForPermissionOn('Change permissions', self.context)
        assert type(retval) in (tuple, list),\
          'retval is a %s, not a tuple or list: %s' % (type(retval), retval) 
        return retval

    @property
    def changePermissionRolesDescription(self):
        return rolesToDescriptions(self.changePermissionRoles)


