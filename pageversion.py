# coding=utf-8
'''Implementation of the Edit Page form.
'''
from datetime import datetime
import pytz
from interfaces import IGSContentPageVersion
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.size.interfaces import ISized

class GSPageVersion(object):
    implements(IGSContentPageVersion)

    # Add type checking. No, seriously, this will cause the fields
    #   in GSPageVersion to be type-checked against the fields in
    #   the schema.
    parentVersion = \
      FieldProperty(IGSContentPageVersion['parentVersion'])
    
    def __init__(self, dataTemplate):
        self.context = self.dataTemplate = dataTemplate

    # ID
    __id_doc = u'ID of the version'
    def get_id(self):
        retval = self.dataTemplate.getId()
        return retval
    def set_id(self, data):
        raise NotImplementedError
    id = property(get_id, set_id, doc=__id_doc)

    # Title
    __title_doc = u'Title of the page'
    def get_title(self):
        retval = getattr(self.dataTemplate, 'title', u'')
        return retval
    def set_title(self, data):
        IGSContentPageVersion['title'].bind(self).validate(data)
        if hasattr(self.dataTemplate, 'title'):
            self.dataTemplate.title = data
        else:
            self.dataTemplate.manage_addProperty('title', data, 
              'ustring')
    title = property(get_title, set_title, doc=__title_doc)

    # Content       
    __content_doc = u'The contents of the page'
    def get_content(self):
        # Zope Five cannot handle Unicode everywhere yet. So we 
        #   ensure that we hand back ASCII, with XML character
        #   references replacing the Unicode characters.
        utext = self.dataTemplate().decode('utf-8')
        assert type(utext) == unicode
        retval = utext.encode('ascii', 'xmlcharrefreplace')
        assert type(retval) == str
        return retval
        
    def set_content(self, data):
        IGSContentPageVersion['content'].bind(self).validate(data)
        self.dataTemplate.write(data)
    content = property(get_content, set_content, doc=__content_doc)

    # Published
    __published_doc = u'If published'
    def get_published(self):
        retval = getattr(self.dataTemplate, 'published', True)
        return retval
    def set_published(self, data):
        IGSContentPageVersion['published'].bind(self).validate(data)
        if hasattr(self.dataTemplate, 'published'):
            self.dataTemplate.published = data
        else:
            self.dataTemplate.manage_addProperty('published', 
              data, 'boolean')
    published = property(get_published, set_published, 
      doc=__published_doc)

    # Editor
    __editor_doc = u'The Editor'
    def get_editor(self):
        retval = getattr(self.dataTemplate, 'editor', '')
        return retval
    def set_editor(self, data):
        IGSContentPageVersion['editor'].bind(self).validate(data)
        if hasattr(self.dataTemplate, 'editor'):
            self.dataTemplate.editor = data
        else:
            self.dataTemplate.manage_addProperty('editor', 
              data, 'ustring')
    editor = property(get_editor, set_editor, 
      doc=__editor_doc)

    # Parent Version
    __parentVersion_doc = u'The version that this is based on'
    def get_parentVersion(self):
        retval = getattr(self.dataTemplate, 'parentVersion', '')
        return retval
    def set_parentVersion(self, data):
        IGSContentPageVersion['parentVersion'].bind(self).validate(data)
        if hasattr(self.dataTemplate, 'parentVersion'):
            self.dataTemplate.parentVersion = data
        else:
            self.dataTemplate.manage_addProperty('parentVersion', 
              data, 'string')
    parentVersion = property(get_parentVersion, set_parentVersion,
      doc=__parentVersion_doc)

    # Creation Date
    __creationDate_doc = u'Creation Date'
    def get_creationDate(self):
        dt = self.id.split('_')[-1]
        y, m, d, h, mi, s = [int(s) for s in 
                            (dt[0:4],  dt[4:6],  dt[6:8], 
                             dt[8:10], dt[10:12], dt[12:])]
        retval = datetime(y,m,d,h,mi,s).replace(tzinfo=pytz.utc)
        return retval
    def set_creationDate(self, data):
        raise NotImplementedError
    creationDate = property(get_creationDate, set_creationDate, 
      doc=__creationDate_doc)

class GSPageVersionSize(object):
    implements(ISized)
    
    def __init__(self, version):
        self.context = self.version = version
        
    def sizeForSorting(self):
        l = len(self.version.content)
        retval = ('byte', l)
        assert len(retval) == 2
        return retval

    def sizeForDisplay(self):
        size = self.sizeForSorting()[1]
        if size < 5000:
            retval = u'%.2fKB' % (size/1024.0)
        elif size < 1000000:
            retval = u'%.1fKB' % (size/1024.0)
        else:
            retval = u'%.2fMB' % (size/(1024*1024.0))

        assert type(retval) == unicode
        return retval

