import os
from interfaces import *
from time import gmtime, time, strftime
from zope.interface import implements, alsoProvides
from zope.component import adapts
from Products.GSContent.interfaces import IGSContentFolder
from Products.GSProfile.utils import enforce_schema
from OFS.OrderedFolder import OrderedFolder
from lxml import etree
from StringIO import StringIO
import interfaces

from page_history import GSPageHistory

class GSContentPage(object):
    """ Wraps a page template to implement a 'content' attribute 
    that formlib can use transparently, even though the content 
    attribute actually maps to the page template content rather than 
    a property on the object"""
    
    implements(IGSContentPage)
    
    CONTENT_TEMPLATE = 'content_en'
    initial_content_file = 'content.html'
    
    def __init__ (self, context, pageId=None):
        self.context = context
        self.pageHistory = GSPageHistory(context)
        
        self.interface = interface = getattr(interfaces, 'IGSContentPage')
        enforce_schema(self.context, IGSContentPage)
        if False: # Fix later
            # If we're adding a new page, create the page then 
            # enforce the schema.
            if pageId:
                # Check that we don't have an existing page with 
                # this ID in the container.
                if hasattr(self.context, pageId):
                    m = 'A page with id %s already exists' % pageId
                    self.status = {'error': True, 'msg': m}
                else:
                    # All good, so create the folder.
                    self.context.manage_addOrderedFolder(pageId)
                    folder = getattr(self.context, pageId)
                    alsoProvides(folder, IGSContentFolder)
                    
                    # Create the content page.
                    content_page = interface(folder)
                    enforce_schema(content_page, IGSContentPage)
                    self.context = folder

                    m = 'Added page with id %s.' % pageId
                    self.status = {'error': False, 'msg': m}

    def new_version_id(self):
        t = strftime("%Y%m%d%H%M%S", gmtime(time()))
        retval = '%s_%s' % (self.CONTENT_TEMPLATE, t)
        assert type(retval) == str
        assert retval
        return retval
        
    def add_to_history (self):
        """ Creates a history entry for the context object """
        history_obj_name = self.new_version_id()
        if not getattr(self.context.aq_explicit, history_obj_name, None):
            content_obj = self.pageHistory.get_current_version()
            assert content_obj
            history_obj = self.context.manage_clone(content_obj, history_obj_name)  
            
            # Add the last editor (as indicated by the last history entry 
            # for the page) as a property on the history entry just 
            # created.
            last_editor = self.get_last_editor()
            history_obj.manage_addProperty('editor', last_editor, 'string')
            
            # If the currently published revision is the latest one, set 
            # the published revision to the newly created historical 
            # revision.
            if getattr(self.context, 'published_revision', None) == content_obj.getId():
                self.context.published_revision = history_obj_name
            
            return history_obj
    
    def copy_revision_to_current (self, revision):
        """ Copy the revision with the specified ID to the current revision """
        assert False, "Replace the call to copy_revision_to_current"  
        assert type(revision) in (str, unicode)
        
        newVersionId = self.new_version_id()
        newVersion = self.context.manage_clone(revision, newVersionId)          

    def publish_revision (self, revision):
        """ Publish the specified revision """
        # Update the published revision
        # --=mpj17=-- Change how publishing works.
        self.published_revision = revision
    
    def get_last_editor (self):
        """ Get the last editor of the context object """
        try:
            # Get the last history entry
            r = self.context._p_jar.db().history(self.context._p_oid, None, 1)
            if r:
                editor = r[0]['user_name'].split(' ')[1]
                return editor
        except:
            return ''
    
    #------------------------------------------------------------------------
    # Properties
    #------------------------------------------------------------------------

    # Content property
    def _setContent(self, value):
        # Save the content to the content object
        template = self.pageHistory.get_current_version()
        if template:
            template.write('<content>%s</content>' % value)
        
    def _getContent(self):
        template = self.pageHistory.get_current_version()
        if template:
            doc = etree.fromstring(template._text)
            tree = doc.xpath('//content/*')
            return ''.join(map(lambda x: etree.tostring(x), tree))
    
    def fix_id (self, id):
        str = ''
        legal = string.digits + string.ascii_lowercase
        id = id.lower()
        for c in range(0, len(id)):
            char = id[c]
            str += legal.find(char) >= 0 and char or ''
        return (str)    

    content = property(_getContent, _setContent)    

    # ID property
    def _setId(self, value):
        try:
            self.context.id = self.fix_id(value)
        except:
            pass
        
    def _getId(self):
        return self.context.id
    
    id = property(_getId, _setId)    

    # Title property
    def _setTitle(self, value):
        try:
            self.context.title = value
        except:
            pass
        
    def _getTitle(self):
        return self.context.title
    
    title = property(_getTitle, _setTitle)    

    # Hidden property
    def _setHidden(self, value):
        try:
            self.context.hidden = value
        except:
            pass
        
    def _getHidden(self):
        return self.context.hidden
    
    hidden = property(_getHidden, _setHidden)    

    # Description property
    def _setDescription(self, value):
        try:
            self.context.description = value
        except:
            pass
        
    def _getDescription(self):
        return self.context.description

    description = property(_getDescription, _setDescription)

    # Published_revision property
    def _setPublishedRevision(self, value):
        try:
            self.context.published_revision = value
        except:
            pass
        
    def _getPublishedRevision(self):
        return self.context.published_revision

    published_revision = property(_getPublishedRevision, _setPublishedRevision)

