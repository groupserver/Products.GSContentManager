import os, zope
from interfaces import *
from zope.interface import implements
from zope.size.interfaces import ISized
from zope.component import adapts, createObject
from Products.GSContent.interfaces import IGSContentFolder
from Products.XWFCore.XWFUtils import munge_date
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from OFS.OrderedFolder import OrderedFolder
from lxml import etree
from StringIO import StringIO
import re
import interfaces

import logging
log = logging.getLogger('GSContentManager')

class GSContentPageHistoryContentProvider(object):
    """ Provides the history of a page """
    
    implements( IGSContentPageHistoryContentProvider )
    adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request
        
        self.pageHistory = GSPageHistory(context)
        
    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)
    #########################################
    # Non standard methods below this point #
    #########################################

    @property
    def history(self):
        return self.get_history()
        
    def get_history (self):
        """ Gets all history entries of the page """
        objects = []
        acl_users = self.context.site_root().acl_users
        items = self.pageHistory.get_versions()
        items.reverse()
        for item in items:
            authorInfo = createObject('groupserver.UserFromId', 
              self.context, item.editor)
            editor = {
              'name' :      authorInfo.name,
              'id':         authorInfo.id,
              'url':        authorInfo.url,
              'anonymous':  authorInfo.anonymous
            }
            entry = {'editor': editor,
                      'size': ISized(item).sizeForDisplay(),
                      'modified': '',
                      'id': item.id,
                      'date': munge_date(self.context, item.creationDate),
                      'published': item.published,
                      'changing': self.changedVersion == item.id
                      }
            objects.append(entry)
            
        return objects

class GSPageHistory(object):
    
    HISTORY_TEMPLATE = 'content_en_%s'
    
    def __init__(self, context):
        self.context = context
        self.histRE = re.compile('content_en_[0-9]{14}')
        self.__keys = None
        
    def get_published_revision (self):
        """ Get the currently published revision of the content
        
        ARGUMENTS
            None
            
        RETURNS
            An XML Template, representing the published revision of
            the content.
            
        SIDE EFFECTS
            None
        """
        assert hasattr(self.context, 'published_revision'),\
            '%s (%s) has no published_revision property' %\
             (self.context, self.context.absolute_url(0))
        pr = getattr(self.context, 'published_revision')

        assert hasattr(self.context, pr), 'No %s in %s (%s)' %\
             (pr, self.context, self.context.absolute_url(0))
        retval = IGSContentPageVersion(getattr(self.context, pr))

        assert retval
        return retval

    @property
    def published(self):
        return self.get_published_revision()
        
    def get_versions(self):
        """Get the versions of the document.
        
        ARGUMENTS
            None
            
        RETURNS
            A list of XML templates, ordered by creation date (newest
            last). Each template represents a version of the content.
            
        SIDE EFFECTS
            None
        """
        templates = self.context.objectValues('XML Template')
        retval = [IGSContentPageVersion(t) for t in templates 
                  if self.histRE.match(t.getId())]
        retval.sort(version_sorter)
        assert type(retval) == list, u'Not a list'
        assert len(retval) > 0, u'List is empty'
        return retval
        
    def get_current_version(self):
        """Get most recently created version of the document content
        
        The current version is the version that was mostly recently
        created, rather than the one that is currently published. The
        latter is returned by "get_published_revision".
        
        ARGUMENTS
            None
            
        RETURNS
            An XML templates that represents the most recent version
            of the content.
            
        SIDE EFFECTS
            None
        """
        retval = self.get_versions()[-1]
        assert retval
        assert hasattr(retval, 'id')
        return retval
        
    @property
    def current(self):
        return self.get_current_version()
    
    # Mapping Methods below
    def keys(self):
        retval = [v.id for v in self.get_versions()  ]
        assert type(retval) == list
        return retval
        
    def values(self):
        return self.get_versions()
        
    def items(self):
        retval = [(v.id, v) for v in self.values()]
        assert type(retval) == list
        return retval
        
    def has_key(self, key):
        return key in self.keys()
    
    def get(self, key, default=None):
        if self.has_key(key):
            retval = [v for v in self.values() if v.id == key][0]
        else:
            retval = default
        return retval
    
    def clear(self):
        raise NotImplementedError
    
    def iterkeys(self):
        return iter(self.keys())

    def itervalues(self):
        return iter(self.values)
        
    def iteritems(self):
        return iter(self.items())
    
    def pop(self):
        raise NotImplementedError
        
    def popitem(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError
    
    def update(self):
        raise NotImplementedError
        
    def __len__(self):
        return len(self.keys())
        
    def __getitem__(self, key):
        if self.has_key(key):
            retval = self.get(key)
        else:
            raise KeyError(key)
        assert retval != None
        return retval
        
    def __setitem__(self, key, value):
        raise NotImplementedError
    
    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        return self.iterkeys()
        
    def __contains__(self, item):
        return self.has_key(item)
        
def version_sorter(a, b):
    assert a
    assert hasattr(a, 'creationDate')
    assert b
    assert hasattr(b, 'creationDate')
    retval = 1
    if a.creationDate < b.creationDate:
        retval = -1
    elif a.creationDate == b.creationDate:
        retval = 0
    assert retval in (-1, 0, 1)
    return retval
    
zope.component.provideAdapter(GSContentPageHistoryContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ContentPageHistory")

