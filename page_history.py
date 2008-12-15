import os, zope
from interfaces import *
from zope.interface import implements
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

    @property
    def history(self):
        return self.get_history()
        
    @property
    def published_revision(self):
        return self.pageHistory.get_published_revision()
        
    #########################################
    # Non standard methods below this point #
    #########################################
    def get_history (self):
        """ Gets all history entries of the page """
        objects = []
        acl_users = self.context.site_root().acl_users
        prev = self.pageHistory.get_published_revision()
        
        for item in self.pageHistory.get_versions():
        
            uid = getattr(item, 'editor', '')
            authorInfo = createObject('groupserver.UserFromId', 
              self.context, uid)
            editor = {
              'name' : authorInfo.name,
              'id':    authorInfo.id,
              'url':   authorInfo.url
            }

            dt = munge_date(self.context, item.bobobase_modification_time())
            size = pretty_size(item.get_size())
            iid = item.getId()
            entry = {'editor': editor,
                      'size': size,
                      'modified': dt,
                      'id': iid,
                      'current': iid == prev
                      }
            objects.append(entry)
            
        return objects

class GSPageHistory(object):
    
    HISTORY_TEMPLATE = 'content_en_%s'
    
    def __init__(self, context):
        self.context = context
        self.histRE = re.compile('content_en_[0-9]{14}')
        
    def get_published_revision (self):
        """ Get the id of the currently published revision """
        assert hasattr(self.context, 'published_revision'),\
            '%s (%s) has no published_revision property' %\
             (self.context, self.context.absolute_url(0))
        pr = getattr(self.context, 'published_revision')

        assert hasattr(self.context, pr), 'No %s in %s (%s)' %\
             (pr, self.context, self.context.absolute_url(0))
        retval = getattr(self.context, pr)

        assert retval
        assert retval.meta_type == 'XML Template' 
        return retval
        
    def get_versions(self):
        """Get the versions of the document.
        """
        templates = self.context.objectValues('XML Template')
        retval = [t for t in templates 
                  if self.histRE.match(t.getId())]
        retval.sort(version_sorter)
        assert type(retval) == list, u'Not a list'
        assert len(retval) > 0, u'List is empty'
        assert ([i.meta_type == 'XML Template' for i in retval]),\
            u'Things other than XML templates returned: %s' % retval
        return retval
        
    def get_current_version(self):
        retval = self.get_versions()[-1]
        assert retval
        assert retval.meta_type == 'XML Template' 
        return retval

def version_sorter(a, b):
    assert a
    assert a.meta_type == 'XML Template'
    assert b
    assert b.meta_type == 'XML Template'
    
    aDt = a.getId().split('_')[2]
    bDt = b.getId().split('_')[2]
    retval = 1
    if aDt < bDt:
        retval = -1
    elif aDt == bDt:
        retval = 0
    assert retval in (-1, 0, 1)
    return retval

def pretty_size(size):
    if size < 5000:
        retval = u'tiny'
    elif size < 1000000:
        retval = u'%sKB' % (size/1024)
    else:
        retval = u'%sMB' % (size/(1024*1024))

    assert type(retval) == unicode
    return retval
    
zope.component.provideAdapter(GSContentPageHistoryContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ContentPageHistory")

