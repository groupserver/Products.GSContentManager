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
        
        cvdt = self.get_current_version().bobobase_modification_time()
        
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

            bbbmt = item.bobobase_modification_time()
            entry = {'editor': editor,
                      'size': item.get_size(),
                      'modified': munge_date(self.context, bbbmt),
                      'id': item.getId(),
                      'current': bbbmt == cvdt
                      }
            objects.append(entry)
        return objects
    
    def get_published_revision (self):
        """ Get the id of the currently published revision """
        return self.context.published_revision
        
    def get_versions(self):
        """Get the verisions of the document.
        """
        retval = [i for i in self.context.objectValues('XML Template')
                  if i.getId()[:11] == self.history_template[:11]]
        retval.sort(bobobase_sorter)
        assert retval
        assert [i.meta_type == 'XML Template' for i in retval]
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
    
zope.component.provideAdapter(GSContentPageHistoryContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ContentPageHistory")

        
