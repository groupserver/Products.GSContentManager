# coding=utf-8
from zope.component import createObject
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface
import zope.component
import zope.publisher.interfaces
import zope.viewlet.interfaces
import zope.contentprovider.interfaces
from Products.XWFCore import XWFUtils
from interfaces import *


class GSContentManagerContextMenuContentProvider(object):
    """GroupServer context-menu for content editing
    """

    zope.interface.implements(IGSContentManagerContextMenuContentProvider)
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
    def __get_global_config(self):
        site_root = self.context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        assert config
        return config

    def get_firstLevelFolder(self, object):
        try:
            while object:
                if (getattr(object.aq_explicit, 'menu_root', 0)
                            or getattr(object.aq_parent.aq_explicit,
                                        'is_division', 0)):
                    return object
                object = object.aq_parent.aq_explicit  # lint:ok
        except:
            return None

    def get_object_values(self, ocontainer, otypes):
        objects = []
        if not ocontainer:
            return objects

        for object_id in ocontainer.objectIds(otypes):
            try:
                object = getattr(ocontainer, object_id)  # lint:ok
                objects.append(object)
            except:
                pass

        return objects

    def compare_url(self, caller, url, exact_match=0):

        request = self.context.REQUEST

        final_path = request.URL0.split(request.BASE0)[1].split('/')[1:]
        virt_path = list(getattr(request, 'VirtualRootPhysicalPath', []))

        curr_path = filter(None, virt_path + final_path)
        nice_url = filter(None, virt_path + str(url).split('/'))

        if exact_match:
            return int(curr_path == nice_url)
        else:
            for i in range(len(nice_url)):
                if i == 0:
                    match = curr_path == nice_url
                else:
                    match = curr_path[:-i] == nice_url
                if match:
                    return 1
            return 0

    def get_division_url(self, nodivision='/'):
        division_object = self.get_division_object()

        if division_object:
            absolute_url = division_object.absolute_url(1)
            if absolute_url == '':
                return absolute_url
            else:
                return '/%s' % division_object.absolute_url(1)
        return no_division

    def get_division_object(self):
        division_object = self.context
        while division_object:
            try:
                division_object = division_object.aq_parent
                if getattr(division_object.aq_inner.aq_explicit,
                            'is_division', 0):
                    break
            except:
                return None

        return division_object.aq_inner.aq_explicit

    def check_has_permission(self, object, permission):
        if not object or not permission:
            return False
        return self.request.AUTHENTICATED_USER.has_permission(permission,
                                                                self.context)

zope.component.provideAdapter(GSContentManagerContextMenuContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ContentManagerContextMenu")
