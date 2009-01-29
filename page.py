import os
from zope.component import adapts, createObject
from interfaces import *
from time import gmtime, time, strftime
from zope.interface import implements, alsoProvides
from zope.component import adapts
from Products.GSContent.interfaces import IGSContentFolder
from Products.GSProfile.utils import enforce_schema
from OFS.OrderedFolder import OrderedFolder
from lxml import etree
from StringIO import StringIO
import interfaces
from Products.Five import BrowserView

from page_history import GSPageHistory


class GSContentPage(BrowserView):
    """The view of a version-controlled content page."""
    
    implements(IGSContentPage)
    
    CONTENT_TEMPLATE = 'content_en'
    initial_content_file = 'content.html'
    
    def __init__(self, context, request):
        assert context
        assert request
        BrowserView.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo',
          context)
        self.pageHistory = GSPageHistory(context)
        self.__userInfo = None
    
    @property
    def userInfo(self):
        if self.__userInfo == None:
            self.__userInfo = createObject('groupserver.LoggedInUser',
              self.context)
        retval = self.__userInfo
        assert retval
        return retval
        
    @property
    def version(self):
        '''The version of the page to display. 
        
        If the user can view the page history then he or she will be
        shown the requested version (set in form.version), or the
        published version of the page.
        
        If the user cannot view the page history then the user will
        be shown only the published version of the page.
        '''
        retval = self.pageHistory.published
        uo = self.userInfo.user
        canViewOld = uo.has_permission('View History', self.context)
        if canViewOld:
            vid = self.request.form.get('form.version',  retval.id)
            retval = self.pageHistory[vid]
        assert retval
        return retval
        
    @property
    def content(self):
        '''Gets the content from the requested version of the page.
        '''
        retval = self.version.content
        assert type(retval) in (str, unicode)
        return retval

    def getId(self):
        '''The ID of the page is the ID of the folder that contains
        the page.
        '''
        return self.context.id
    
    @property
    def title(self):
        '''Gets the title from the requested version of the page.
        '''
        retval = self.version.title
        assert type(retval) in (str, unicode)
        return retval

    @property
    def hidden(self):
        '''Returns the hidden value of the *entire* folder, not the
        version.
        '''
        retval = self.context.hidden
        assert type(retval) == bool
        return retval
                
    @property
    def editor(self):
        '''Returns the name of the last editor.
        '''
        retval = self.version.editor
        assert type(retval) in (str, unicode)
        return retval

