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
from Products.XWFCore import XWFUtils
import interfaces

def wym_editor_widget(field, request):
    retval = TextAreaWidget(field, request)
    retval.cssClass = 'wymeditor'
    return retval

class EditPageForm(PageForm):
    label = u'Edit Page'
    pageTemplateFileName = 'browser/templates/edit_page.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        # Adapt the context object to a content page object
        self.interface = interface = getattr(interfaces, 'IGSContentPage')
        self.context = self.content_page = interface(context)
        self.request = request

        PageForm.__init__(self, self.content_page.context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', self.content_page.context)
        site_root = self.content_page.context.site_root()

        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        
        self.form_fields = form.Fields(interface, render_context=True, omit_readonly=True)

        self.form_fields['content'].custom_widget = wym_editor_widget
        
    @property
    def id(self):
        return self.content_page.id

    @property
    def title(self):
        return self.content_page.title
    
    @property
    def description(self):
        return self.content_page.description

    @property
    def content(self):
        return self.content_page.content
    
    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Edit" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Edit', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        return self.set_data(data)
        
    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def set_data(self, data):
        assert self.context
        assert self.form_fields

        alteredFields = []
        for datum in getFieldsInOrder(self.interface):
            if data.has_key(datum[0]):
                if data[datum[0]] != getattr(self.context, datum[0]):
                    alteredFields.append(datum[0])
        
        # If the page ID has changed, we need to rename the page and redirect to
        # the new page in edit mode.
        try:
            new_id = data[alteredFields[alteredFields.index('id')]]
        except:
            new_id = None
       
        page_renamed = False
        if new_id:
            try:
                current_id = self.content_page.id
                folder = self.content_page.context.aq_parent
                if getattr(folder.aq_explicit, new_id, None):
                    self.status = u'A page with ID \'%s\' already exists here' % new_id
                    return
    
                folder.manage_renameObject(current_id, new_id)
                new_page = getattr(folder.aq_explicit, new_id, None)
                self.content_page.context = new_page
                page_renamed = True
            except:
                self.status = u'There was problem renaming this page'
                return
                                
        # Handle publishing of a selected revision.
        published_revision = self.request.get('published_revision', None)
        if published_revision:
            self.content_page.copy_revision_to_current(published_revision)
            self.status = u'Revision %s has been copied to the current revision and published.' % published_revision
            return
        else:
            # Save the current revision in the history
            self.content_page.add_to_history()    
        
            # Update the content object
            changed = form.applyChanges(self.context, self.form_fields, data)
        
        # If we've renamed the page, redirect to the new edit page URL.
        if page_renamed:
            self.request.response.redirect('%s/%s' % (new_page.absolute_url(0), 'edit_page.html'))
            return
        
        if changed:
            fields = [self.interface.get(name).title
                      for name in alteredFields]
            f = ' and '.join([i for i in (', '.join(fields[:-1]), fields[-1])
                              if i])
            self.status = u'Changed %s' % f
        else:
            self.status = u"No fields changed."
        assert self.status
        assert type(self.status) == unicode
