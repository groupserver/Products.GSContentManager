# coding=utf-8
'''Implementation of the Edit Page form.
'''
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
from Products.XWFCore.XWFUtils import comma_comma_and
from interfaces import IGSContentPage, IGSEditContentPage
from page import GSContentPage
from audit import PageEditAuditor, EDIT_CONTENT, RENAME_PAGE
from page_history import GSPageHistory

import logging
log = logging.getLogger('GSContentManager')

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

        self.ev = ev = request.form.get('form.edited_version', 
            hist.current.getId())
        assert ev in hist, u'%s not in %s' % (ev, hist.keys())
        print 'Editing %s:\n%s' % (ev, hist[ev]())
        request.form['form.content'] = hist[ev]()

        self.form_fields = form.Fields(IGSEditContentPage, 
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

    # @form.action(label=u'Rename', failure='action_failure')
    def handle_rename(self, action, data):
        self.auditor = PageEditAuditor(self.context)
        self.rename_page(data)
        # If the page ID has changed, we need to rename the folder
        # and redirect to the new folder (in edit mode).
        new_id = data['id']
        oldUri = self.context.absolute_url(0)
        try:
            r = self.rename_page(new_id)
        except e:
            self.status = u'There was problem renaming this page'
        else:
            # --=mpj17=-- ok?
            uri = '%s/edit_page.html' % self.folder.absolute_url(0)
            self.auditor.log(RENAME_PAGE, oldUri, uri)
            self.request.response.redirect(uri)

    def rename_page(self, newId):
        current_id = self.id
        parentFolder = self.context.aq_parent
        if hasattr(parentFolder.aq_explicit, new_id):
            self.status = u'<a href="%s">A page with identifier '\
            '<code class="page">%s</code></a> already exists '\
            u'in this folder' % (new_id, new_id)
            retval = None
        else:
            folder.manage_renameObject(current_id, new_id)
            retval = getattr(folder.aq_explicit, new_id, None)
            newURL = retval.absolute_url(0)
            self.status = 'Page renamed'
        return retval
    
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
    
    @form.action(label=u'Edit', failure='action_failure')
    def handle_set(self, action, data):
        '''Change the data that is being 
        '''
        #return self.set_data(data)
        print self.content
        self.satus = u'Foo'

    def set_data(self, data):
        assert self.folder
        assert self.form_fields
        #content_page = IGSContentPage(self.folder)
        #assert IGSContentPage.implementedBy(content_page),\
        #  '%s does not implement IGSContentPage' % content_page

        fields = []
        for datum in getFieldsInOrder(IGSContentPage):
            if data.has_key(datum[0]):
                if data[datum[0]] != getattr(self.context, datum[0]):
                    fields.append(datum[0])
        if fields:
            # Save the new version in the history
            # 1. Figure out the version that is being edited
            currentVersionId = datum['edited_version'] #--=mpj17=-- Better be set
            # 2. Copy that to a new revision
            newVersion = self.new_version(currentVersion)
            # 3. Apply changes
            changed = form.applyChanges(newVersion, self.form_fields, data)

            fieldNames = [IGSContentPage.get(name).title
                      for name in alteredFields]
            self.status = u'Changed %s' % comma_comma_and(fieldNames)
            if 'content' in fields:
                self.auditor.info(EDIT_CONTENT)
            if ((len(fields) == 1) and ('content' not in fields)) or\
                (len(fields) > 1):
                self.auditor.info(EDIT_ATTRIBUTE)
        else:
            self.status = u'No changes made to this page.'
            
        assert self.status
        assert type(self.status) == unicode

    def new_version(self, currentVersionId):
        pass

