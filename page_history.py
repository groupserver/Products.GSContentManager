import os, zope
from interfaces import *
from zope.interface import implements
from zope.component import adapts
from Products.GSContent.interfaces import IGSContentFolder
from Products.XWFCore.XWFUtils import munge_date
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from OFS.OrderedFolder import OrderedFolder
from lxml import etree
from StringIO import StringIO
import interfaces

class GSContentPageHistoryContentProvider(object):
    """ Provides the history of a page """
    
    implements( IGSContentPageHistoryContentProvider )
    adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)
    
    content_template = 'content_en'
    history_template = 'content_en_%s'
    
    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request
        
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
        return self.get_published_revision()
        
    #########################################
    # Non standard methods below this point #
    #########################################
    def get_history (self):
        """ Gets all history entries of the page """
        objects = []
        acl_users = self.context.site_root().acl_users
        prev = self.get_published_revision()
        
        for item in self.get_versions():
        
            uid = getattr(item, 'editor', '')
            user = uid and acl_users.getUser(uid) or None
            if user:
                editor = {
                  'name' : user.getProperty('fn', ''),
                  'id':    uid,
                  'url':  '/contacts/%s' % uid
                }
            else:
               editor = {
                  'name' : u'No user',
                  'id':    '',
                  'url':  ''
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
    
    def get_published_revision (self):
        """ Get the id of the currently published revision """
        prev = self.context.published_revision
        if not prev:
            return self.content_template
        else:
            return prev
        
    def get_versions(self):
        """Get the versions of the document.
        """
        retval = [i for i in self.context.objectValues('XML Template')
                  if i.getId()[:10] == self.history_template[:10]]
        
        if len(retval) == 0:
            return retval
        
        retval.sort(bobobase_sorter)
        if retval[0].bobobase_modification_time() < \
           retval[-1].bobobase_modification_time():
           retval.reverse()
        assert (retval and [i.meta_type == 'XML Template' for i in retval])\
          or (retval == [])
        return retval
        
    def get_current_version(self):
        self.context.objectValues('XML Template')
        retval = [i for i in self.context.objectValues('XML Template')
                  if i.getId() == self.content_template]
        retval = retval[0]
        assert retval
        return retval
        
def bobobase_sorter(a, b):
    assert a
    assert a.bobobase_modification_time
    assert b
    assert b.bobobase_modification_time
    
    ta = a.bobobase_modification_time()
    tb = b.bobobase_modification_time()
    
    retval = 0
    if a > b:
        retval = -1
    elif a < b:
        retval = 1
            
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

        
