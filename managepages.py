# coding=utf-8
'''Implementation of the Edit Page form.
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

        # I set this here, because Zope hates me later.
        self.pageTree = PageTree(folder)
        
        self.auditor = None
    
    @form.action(label=u'Add', failure='action_failure')
    def handle_add(self, action, data):
        newPage = data.get('pageId', '')
        assert newPage
        assert not(hasattr(self.folder, newPage)), \
          '%s already in %s' % (newPage, self.folder.getId())
        self.folder.manage_addFolder(newPage)

        newFolder = getattr(self.folder, newPage)
        assert newFolder, '%s not in %s' %\
          (newPage, self.folder.getId())
        add_marker_interfaces(newFolder, 
          ('Products.GSContentManager.interfaces.IGSContentManagerFolderMarker',))

        nvId = new_version_id()
        newVersion = new_version(newFolder, nvId)
        newVersion.content = \
          u'<p> </p>'
        newVersion.title = data.get('title', '').encode('utf-8')
        newFolder.manage_addProperty('published_revision', nvId, 
          'string')
        
        self.status = u'Added <a href="%s">%s</a>.' %\
          (newPage, data.get('title', ''))
        assert type(self.status) == unicode
        assert self.status

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
        # <rant author="mpj17">
        #   I should be using IContainerItemRenamer here, but some 
        #   web-footed drool factory did not implement the "get"
        #   method, even though the Drool Factory did state that
        #   the folder implements IContainer.
        #</rant>
        oldName = self.folder.getId()
        parent = self.folder.aq_inner.aq_parent
        assert hasattr(parent, oldName), '%s not in %s' %\
          (oldName, parent.getId())
        newName = data.get('renamedPageId', '')
        assert not(hasattr(parent, newName)), '%s already in %s' %\
          (newName, parent.getId())
        parent.manage_renameObject(oldName, newName, None)
        assert hasattr(parent, newName), \
          '%s not renamed to %s in %s' % \
          (oldName, newName, parent.getId())
        self.status = u'Renamed <code>%s</code> to <code>%s</code>.'%\
          (oldName, newName)
        assert type(self.status) == unicode
        assert self.status

    def nodeId_to_url(self, nodeId):
        retval = '-'.join(nodeId.split('-')[1:])
        retval = retval.replace('-', '/').replace('//', '-')
        retval = 'http://%s' % retval
        assert retval
        return retval
        
    @form.action(label=u'Move', failure='action_failure')
    def handle_move(self, action, data):
        source = self.folder.absolute_url()
        destination = self.nodeId_to_url(data['moveDestination'])
        if source == destination:
            self.status = u'Cannot move a page '\
              u'(<code><a href="%(src)s">%(src)s</a></code>) '\
              u'to itself.' %\
              {'src': source, 'dest': destination}
        elif source in destination:
            self.status = u'Cannot move a parent-page '\
              u'(<code><a href="%(src)s">%(src)s</a></code>) '\
              u'into a child page '\
              u'(<code><a href="%(dest)s">%(dest)s</a></code>).' %\
              {'src': source, 'dest': destination}
        else:
            # Cut the source
            sourceFolder = \
              self.get_folder_from_id(url_to_nodeId('foo-', source))
            srcParent = sourceFolder.aq_parent
            cut = srcParent.manage_cutObjects([sourceFolder.getId()], 
                None)
            # Paste into the destination
            destinationFolder = \
              self.get_folder_from_id(data['moveDestination'])
            destinationFolder.manage_pasteObjects(cut, None)
            self.status = u'Moved '\
              u'(<code><a href="%(src)s">%(src)s</a></code>) '\
              u'to '\
              u'(<code><a href="%(dest)s">%(dest)s</a></code>).' %\
              {'src': source, 'dest': destination}
        assert type(self.status) == unicode
        assert self.status

    def get_folder_from_id(self, folderId):
        folders = folderId.split('-')
        # Feel the hate of Zope (see __init__)
        rootId = self.pageTree.tree[0].getId()
        while folders[0] != rootId:
            folders = folders[1:]
        folder = self.context
        for folderId in folders:
            folder = getattr(folder, folderId)
        retval = folder
        return retval

    def action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

