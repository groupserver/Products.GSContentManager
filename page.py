import os
from interfaces import *
from time import gmtime, time, strftime
from zope.interface import implements, alsoProvides
from zope.component import adapts
from Products.GSContent.interfaces import IGSContentFolder
from OFS.OrderedFolder import OrderedFolder
from lxml import etree
from StringIO import StringIO
import interfaces

class GSContentPage(object):
    """ Wraps a page template to implement a 'content' attribute that formlib can use transparently, 
    even though the content attribute actually maps to the page template content rather than a property
    on the object"""
    
    implements(IGSContentPage)
    
    content_template = 'content_en'
    initial_content_file = 'content.html'
    
    def __init__ (self, context, mode='edit', id=None):
        
        self.status = {'error': False}
        self.context = context
        self.interface = interface = getattr(interfaces, 'IGSContentPage')

        if mode == 'edit':
            # If we're editing an existing page, just enforce the schema.
            self.enforce_schema(IGSContentPage)
        elif mode == 'add':
            # If we're adding a new page, create the page then enforce the schema.
            if id:
                # Check that we don't have an existing page with this ID in the
                # container.
                if getattr(self.context, id, None):
                    self.status = {'error': True, 'msg': 'A page with id %s already exists' % id}
                    return
                
                # All good, so create the folder.
                self.context.manage_addOrderedFolder(id)
                folder = getattr(self.context, id)
                alsoProvides(folder, IGSContentFolder)
                
                # Create the content page.
                content_page = interface(folder)
                content_page.enforce_schema(IGSContentPage)
                self.context = folder
    
    def enforce_schema(self, schema):
        """
        SIDE EFFECTS
          * "inputData" is stated to provide the "schema" interface
          * "inputData" will provide all the properties defined in "schema"
        """
        typeMap = {
          Text:      'ulines',
          TextLine:  'ustring',
          ASCII:     'lines',
          ASCIILine: 'string',
          URI:       'string',
          Bool:      'boolean',
          Float:     'float',
          Int:       'int',
          Datetime:  'date',
          Date:      'date',
        }
        fields = [field[0] for field in getFieldsInOrder(IGSContentPage)]
        for field in fields:
            if field != 'content':
                if not hasattr(self.context, field):
                    default = schema.get(field).default or ''
                    t = typeMap.get(type(schema.get(field)), 'ustring')
                    self.context.manage_addProperty(field, default, t)
                    
        # Make sure a content page template exists.
        if not getattr(self.context.aq_explicit, self.content_template, None):
            template_path = os.path.dirname(os.path.realpath(__file__))
            filename = os.path.join(os.path.join(template_path, 'config'), self.initial_content_file)
            self.context.manage_addProduct['DataTemplates'].manage_addXMLTemplate(self.content_template, file(filename))

    def add_to_history (self):
        """ Creates a history entry for the context object """
        history_obj_name = '%s_%s' % (self.content_template, strftime("%Y%m%d%H%M%S", gmtime(time())))
        if not getattr(self.context.aq_explicit, history_obj_name, None):
            content_obj = getattr(self.context.aq_explicit, self.content_template, None)
            assert content_obj
            history_obj = self.context.manage_clone(content_obj, history_obj_name)  
            
            # Add the last editor (as indicated by the last history entry for the page)
            # as a property on the history entry just created.
            last_editor = self.get_last_editor()
            history_obj.manage_addProperty('editor', last_editor, 'string')
            
            # If the currently published revision is the latest one, set the published revision to the
            # newly created historical revision.
            if getattr(self.context, 'published_revision', None) == self.content_template:
                self.context.published_revision = history_obj_name
            
            return history_obj
    
    def copy_revision_to_current (self, revision):
        """ Copy the revision with the specified ID to the current revision """

        # Move the current object to a revision.
        self.add_to_history()

        # Copy the contents of the specified revision to the current revision
        rev_template = getattr(self.context.aq_explicit, revision, None)

        if rev_template:
            content_obj = getattr(self.context.aq_explicit, self.content_template, None)
            content_obj.write(rev_template._text)

        # Update the published revision
        self.published_revision = self.content_template
    
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
        template = getattr(self.context, self.content_template, None)
        if template:
            template.write('<content>%s</content>' % value)
        
    def _getContent(self):
        template = getattr(self.context, self.content_template, None)
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
