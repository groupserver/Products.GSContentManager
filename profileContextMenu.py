from zope.component import createObject
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface, zope.component, zope.publisher.interfaces
import zope.viewlet.interfaces, zope.contentprovider.interfaces 
from Products.XWFCore import XWFUtils, ODict
from interfaces import *

class GSContentManagerContextMenuContentProvider(object):
    """GroupServer context-menu for the user profile area.
    """

    zope.interface.implements( IGSContentManagerContextMenuContentProvider )
    zope.component.adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request

        
    def update(self):
        self.__updated = True

        self.siteInfo = createObject('groupserver.SiteInfo', 
          self.context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', 
          self.context)

        self.__pages__ = self.get_pages()

        self.requestBase = self.request.URL.split('/')[-1]
        self.userId = self.context.getId()
        self.userName = XWFUtils.get_user_realnames(self.context)

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)
        
    #########################################
    # Non standard methods below this point #
    #########################################
    def get_pages(self):
        assert self.view
        config = self.__get_global_config()
        showEmail = config.getProperty('showEmailAddressTo','nobody')
        showEmail = showEmail.lower()
        
        if (self.viewingUser.has_role('Authenticated')
            and (self.context.getId() == self.viewingUser.getId())):
            return self.get_edit_pages()
        elif (self.viewingUser.has_role('Authenticated')
            and (showEmail == 'request')):
            return self.get_request_pages()
        else:
            return ODict()

    def __get_global_config(self):
        site_root = self.context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        assert config
        return config        
    def get_edit_pages(self):
        pages = ODict()
        pages['edit.html']     = 'Edit Profile'
        pages['image.html']    = 'Edit Image'
        pages['useremail']     = 'Edit Email Settings'
        pages['password.html'] = 'Set Password'
        return pages        

    def get_request_pages(self):
        pages = ODict()
        pages['user-request-contact'] = 'Request Contact'
        return pages
        
    @property
    def viewingUser(self):
        assert hasattr(self, 'request')
        assert hasattr(self.request, 'AUTHENTICATED_USER')
        retval = self.request.AUTHENTICATED_USER
        return retval
    
    @property
    def userUrl(self):
        retval = '/contacts/%s' % self.userId
        assert type(retval) == str
        assert retval
        return retval

    @property
    def pages(self):
        return self.__pages__
        
    def page_is_current(self, pageId):
        return self.requestBase == pageId

    def pageClass(self, pageId):
        if self.page_is_current(pageId):
            retval = 'current'
        else:
            retval = 'not-current'
        assert retval
        return retval

zope.component.provideAdapter(GSContentManagerContextMenuContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ProfileContextMenu")

