# coding=utf-8
'''Implementation of the Edit Page form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject, adapts
from zope.component.interfaces import IFactory
from zope.interface import implements, providedBy, implementedBy,\
  directlyProvidedBy, alsoProvides
from zope.formlib import form
from zope.copypastemove.interfaces import *
from zope.copypastemove import ItemNotFoundError
from zope.exceptions import DuplicationError
from zope.app.container.interfaces import IContainer, IOrderedContainer
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import MultiCheckBoxWidget, SelectWidget,\
  TextAreaWidget
from zope.app.apidoc.interface import getFieldsInOrder
from zope.schema import *
from Products.XWFCore.XWFUtils import comma_comma_and, munge_date
from interfaces import *

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
        self.status = u'Should add'
        assert type(self.status) == unicode
        assert self.status
        return retval

    @form.action(label=u'Copy', failure='action_failure')
    def handle_copy(self, action, data):
        copier = IObjectCopier(self.folder)
        assert copier.copyable()
        self.status = u'Should copy!'
        assert type(self.status) == unicode
        assert self.status
        return retval

    @form.action(label=u'Rename', failure='action_failure')
    def handle_rename(self, action, data):

        f = IContainer(self.context)
        parent = f.aq_inner.aq_parent
        renamer = IContainerItemRenamer(parent)
        oldName = self.folder.getId()
        newName = data.get('renamedPageId', '')
        if newName:
            try:
                # --=mpj17=-- I *do* know how to use try-except 
                #    blocks; I preferr forward error-detection :P
                renamer.renameItem(oldName, newName)
            except ItemNotFoundError, e:
                self.status = u'Could not find <code>%s</code>.' %\
                  oldName
            except DuplicationError, e:
                self.status = u'There is already a page with the ' \
                  u'identifier <code>%s</code> in <code>%s</code>.' %\
                  (oldName, newName)
            else:
                self.status = u'Should rename!'
        else:
            self.status = u'Name not specified'
        assert type(self.status) == unicode
        assert self.status
        return retval

    @form.action(label=u'Move', failure='action_failure')
    def handle_move(self, action, data):
        mover = IObjectMover(self.folder)
        assert mover.movable()
        self.status = u'Should move!'
        assert type(self.status) == unicode
        assert self.status
        return retval

    def action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

