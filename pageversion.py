# coding=utf-8
'''Implementation of the Edit Page form.
'''
from interfaces import IGSContentPageVersion
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

class GSPageVersion(object):
    implements(IGSContentPageVersion)

    # Add type checking. No, seriously, this will cause the fields
    #   in GSPageVersion to be type-checked against the fields in
    #   the schema.
    id = FieldProperty(IGSContentPageVersion['id'])
    title = FieldProperty(IGSContentPageVersion['title'])
    content = FieldProperty(IGSContentPageVersion['content'])
    published = FieldProperty(IGSContentPageVersion['published'])
    editor = FieldProperty(IGSContentPageVersion['editor'])
    parentVersion = \
      FieldProperty(IGSContentPageVersion['parentVersion'])
    
    def __init__(self, xmlDataTemplate):
        self.context = self.xmlDataTemplate = xmlDataTemplate

        # Most fields are based on the XML data template that is
        #   being adapted
        self.id = self.xmlDataTemplate.getId()
        self.title = getattr(self.xmlDataTemplate, 'title', '')
        # Except "content" which is delt with below
        self.published = getattr(self.xmlDataTemplate, 'published', 
          False)
        self.editor = getattr(self.xmlDataTemplate, 'editor', '')
        self.parentVersion = getattr(self.xmlDataTemplate,
          'parentVersion', '')

    # Content       
    def get_content(self):
        retval = self.xmlDataTemplate()
        return retval
    def set_content(self, data):
        self.xmlDataTemplate.write(data)
    __content_doc = u'The contents of the page'
    content = property(get_content, set_content, doc=__content_doc)

