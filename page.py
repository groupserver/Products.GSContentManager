import os
from interfaces import *
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

    # Title property
    def _setVisible(self, value):
        try:
            self.context.visible = value
        except:
            pass
        
    def _getVisible(self):
        return self.context.visible
    
    visible = property(_getVisible, _setVisible)    

    # Description property
    def _setDescription(self, value):
        try:
            self.context.description = value
        except:
            pass
        
    def _getDescription(self):
        return self.context.description

    description = property(_getDescription, _setDescription)
