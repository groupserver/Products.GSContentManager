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
        for item in self.context.objectValues():
            if item.meta_type == 'XML Template':
                uid = getattr(item, 'editor', '')
                user = uid and acl_users.getUser(uid) or None
                editor = {
                  'name' : u'No user',
                  'id':    '',
                  'url':  ''
                }
                if user:
                    editor = {
                      'name' : user.getProperty('fn', ''),
                      'id':    uid,
                      'url':  '/contacts/%s' % uid
                    }
                d = munge_date(self.context, 
                               item.bobobase_modification_time())
                entry = {'editor': editor,
                         'size': item.get_size(),
                         'modified': d,
                         'id': item.getId()
                         }
                if item.getId() == self.content_template:
                    current = entry
                else:
                    objects.append(entry)

        # Append the current template so it's at the top when reverse sorted.
        objects.append(current)

        objects.reverse()
        return objects
    
    def get_published_revision (self):
        """ Get the id of the currently published revision """
        return self.context.published_revision
        
zope.component.provideAdapter(GSContentPageHistoryContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ContentPageHistory")

        
