# coding=utf-8
'''Implementation of the Edit Page form.
'''
from __future__ import absolute_import, unicode_literals
from zope.interface import implementer
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore.XWFUtils import add_marker_interfaces
from gs.content.form.base import SiteForm
from .interfaces import IGSMangePages, IGSContentPageVersion
from .utils import new_version_id, new_version
from .pagetree import PageTree, url_to_nodeId


@implementer(IGSContentPageVersion)
class ManagePagesForm(SiteForm):
    label = 'Manage Pages'
    pageTemplateFileName = 'browser/templates/manage_pages.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSMangePages, render_context=False,
                                omit_readonly=False)

    def __init__(self, folder, request):
        super(ManagePagesForm, self).__init__(folder, request)
        self.folder = folder

        # I set this here, because Zope hates me later.
        self.pageTree = PageTree(folder)

        self.auditor = None

    @form.action(label='Add', failure='action_failure')
    def handle_add(self, action, data):
        newPage = data.get('pageId', '')
        assert newPage
        assert not(hasattr(self.folder, newPage)), \
          '%s already in %s' % (newPage, self.folder.getId())
        self.folder.manage_addFolder(newPage)

        newFolder = getattr(self.folder, newPage)
        assert newFolder, '%s not in %s' % (newPage, self.folder.getId())
        markerName = \
             'Products.GSContentManager.interfaces.'\
             'IGSContentManagerFolderMarker'
        add_marker_interfaces(newFolder, (markerName,))

        nvId = new_version_id()
        newVersion = new_version(newFolder, nvId)
        newVersion.content = \
          '<p> </p>'
        newVersion.title = data.get('title', '').encode('utf-8')
        newFolder.manage_addProperty('published_revision', nvId,
          'string')

        self.status = 'Added <a href="%s">%s</a>.' %\
          (newPage, data.get('title', ''))
        assert self.status

    @form.action(label='Copy', failure='action_failure')
    def handle_copy(self, action, data):
        source = self.folder.absolute_url()

        # Copy the source
        sourceFolder = \
          self.get_folder_from_id(url_to_nodeId('foo-', source))
        srcParent = sourceFolder.aq_parent
        copy = srcParent.manage_copyObjects([sourceFolder.getId()],
            None)

        # Paste into the destination
        #destination = self.nodeId_to_url(data['copyDestination'])
        destinationFolder = \
          self.get_folder_from_id(data['copyDestination'])
        pasteResult = destinationFolder.manage_pasteObjects(copy, None)

        # Rename
        copyId = pasteResult[0]['new_id']
        newId = data['newPageId']
        destinationFolder.manage_renameObject(copyId, newId, None)
        copied = getattr(destinationFolder, newId).absolute_url()

        self.status = 'Copied '\
          '(<code><a href="%(src)s">%(src)s</a></code>) '\
          'to '\
          '(<code><a href="%(dest)s">%(dest)s</a></code>).' %\
          {'src': source, 'dest': copied}
        assert self.status

    @form.action(label='Rename', failure='action_failure')
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
        self.status = 'Renamed <code>%s</code> to <code>%s</code>.' % \
          (oldName, newName)
        assert self.status

    def nodeId_to_url(self, nodeId):
        retval = '-'.join(nodeId.split('-')[1:])
        retval = retval.replace('-', '/').replace('//', '-')
        retval = 'http://%s' % retval
        assert retval
        return retval

    @form.action(label='Move', failure='action_failure')
    def handle_move(self, action, data):
        source = self.folder.absolute_url()
        destination = self.nodeId_to_url(data['moveDestination'])
        if source == destination:
            self.status = 'Cannot move a page '\
              '(<code><a href="%(src)s">%(src)s</a></code>) '\
              'to itself.' %\
              {'src': source, 'dest': destination}
        elif source in destination:
            self.status = 'Cannot move a parent-page '\
              '(<code><a href="%(src)s">%(src)s</a></code>) '\
              'into a child page '\
              '(<code><a href="%(dest)s">%(dest)s</a></code>).' %\
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
            self.status = 'Moved '\
              '(<code><a href="%(src)s">%(src)s</a></code>) '\
              'to '\
              '(<code><a href="%(dest)s">%(dest)s</a></code>).' %\
              {'src': source, 'dest': destination}
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
            self.status = '<p>There is an error:</p>'
        else:
            self.status = '<p>There are errors:</p>'
