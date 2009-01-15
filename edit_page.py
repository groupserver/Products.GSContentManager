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
        
        # Get the version of the page for editing
        self.hist = GSPageHistory(folder)
        ev = request.form.get('form.edited_version', 
            self.hist.current.getId()) #--=mpj17=-- Check manual
        assert ev in self.hist, \
          u'%s not in %s' % (ev, self.hist.keys())
        self.versionForChange = IGSContentPageVersion(self.hist[ev])
        
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
        i, s = self.get_auditDatums(self.versionForChange, newVersion)
        self.auditor.info(EDIT_CONTENT, i, s)
        self.status = u'Changed %s' % data['title']
        assert self.status
        assert type(self.status) == unicode

    def new_version(self):
        '''Create a new (blank) version of the document'''
        newId = self.new_version_id()
        manageAdd = self.folder.manage_addProduct['DataTemplates']
        manageAdd.manage_addXMLTemplate(newId, None)
        xmlDataTemplate = getattr(self.folder, newId)
        retval = IGSContentPageVersion(xmlDataTemplate)
        assert retval
        assert retval.getId() == newId
        assert retval.meta_type == 'XML Template'
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
        title = oldVer.title_or_id()
        instanceDatum = u','.join((b64encode(url), b64encode(title),
            b64encode(oldVer.getId()), b64encode(newVer.getId())))

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
        dt = ver.getId().split('_')[-1]
        y, m, d, h, mi, s = [int(s) for s in 
                            (dt[0:4],  dt[4:6],  dt[6:8], 
                             dt[8:10], dt[10:12], dt[12:])]
        vDate = datetime(y,m,d,h,mi,s).replace(tzinfo=pytz.utc)
        vUI = createObject('groupserver.UserFromId', 
                            self.folder, ver.editor)
        retval = u'%s (%s)' % (userInfo_to_anchor(vUI),
                               munge_date(self.folder, vDate,'%Y %b %d %H:%M:%S'))
        assert retval
        assert type(retval) == unicode
        return retval 

