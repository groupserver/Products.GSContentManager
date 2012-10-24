from zope.component import createObject
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface
import zope.component
import zope.publisher.interfaces
import zope.viewlet.interfaces
import zope.contentprovider.interfaces
from interfaces import *
from zope.app.publisher.browser.menu import getMenu

from AccessControl.security import newInteraction

import logging
log = logging.getLogger('GSContentManagerTabMenuContentProvider')


class GSContentManagerTabMenuContentProvider(object):
    """GroupServer tab-menu for the content manager.
    """

    zope.interface.implements(IGSContentManagerTabMenuContentProvider)
    zope.component.adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request
        self.__userInfo = None

        newInteraction()

    def update(self):
        self.__updated = True

        self.siteInfo = createObject('groupserver.SiteInfo',
          self.context)
        self.groupsInfo = createObject('groupserver.GroupsInfo',
          self.context)

        self.pages = getMenu('page_change_menu', self.context,
          self.request)

        self.requestBase = self.request.URL.split('/')[-1]

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)

    #########################################
    # Non standard methods below this point #
    #########################################

    def page_class(self, page):
        if page['selected']:
            retval = 'ui-state-default ui-corner-top '\
                        'ui-tabs-selected ui-state-active'
        else:
            retval = 'ui-state-default ui-corner-top'
        assert retval
        return retval

    @property
    def show(self):
        uo = self.userInfo.user

        p = uo.has_permission('Manage properties', self.context)
        mp = p is not None

        p = uo.has_permission('View history', self.context)
        vh = p is not None

        retval = mp or vh
        assert type(retval) == bool, \
          'Returning %s, not bool.' % retval
        return retval

    @property
    def userInfo(self):
        if self.__userInfo is None:
            self.__userInfo = createObject('groupserver.LoggedInUser',
              self.context)
        retval = self.__userInfo
        assert retval
        return retval


zope.component.provideAdapter(GSContentManagerTabMenuContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ContentManagerTabMenu")
