import os
from interfaces import *
from zope.interface import implements, alsoProvides
from zope.component import adapts
from Products.GSContent.interfaces import IGSContentFolder
from OFS.OrderedFolder import OrderedFolder
from lxml import etree
from StringIO import StringIO
import interfaces

class GSContentPageHistoryContentProvider(object):
    """ Provides the history of a page """
    
    implements(IGSContentPageHistory)
    zope.interface.implements( IGSContentPageHistoryContentProvider )
    zope.component.adapts(zope.interface.Interface,
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

    #########################################
    # Non standard methods below this point #
    #########################################
    def get_history (self):
        """ Gets all history entries of the page """
        objects = []
        for item in self.context.objectValues():
            if item.meta_type != 'XML Template' and item.getId() != self.content_template:
                entry = {'editor': 'editor',
                         'size': 'size',
                         'modified': 'modified'
                         }
                objects.append(entry)
                
        return objects
    
    @property
    def history(self):
        return self.get_history()
        
zope.component.provideAdapter(GSContentPageHistoryContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ContentPageHistory")

        
