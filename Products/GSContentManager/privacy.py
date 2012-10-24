# coding=utf-8
from AccessControl.PermissionRole import rolesForPermissionOn
from zope.interface import implements, Interface
from zope.component import adapts, provideAdapter
from zope.contentprovider.interfaces import UpdateNotCalled, IContentProvider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from interfaces import IGSContentPagePrivacyContentProvider
from utils import rolesToDescriptions


class GSContentPagePrivacyContentProvider(object):
    """ Provides the privacy description of a page """

    implements(IGSContentPagePrivacyContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request
        self.privacy = None

    def update(self):
        self.__updated = True
        self.privacy = GSPagePrivacy(self.context)

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)
    #########################################
    # Non standard methods below this point #
    #########################################

    def rolesToDescriptions(self, roles):
        return rolesToDescriptions(roles)


class GSPagePrivacy(object):

    def __init__(self, context):
        self.context = context

    @property
    def viewRoles(self):
        retval = rolesForPermissionOn('View', self.context)
        assert type(retval) in (tuple, list),\
          'retval is a %s, not a tuple or list: %s' % (type(retval), retval)
        return retval

    @property
    def changeRoles(self):
        retval = rolesForPermissionOn('Manage properties', self.context)
        assert type(retval) in (tuple, list),\
          'retval is a %s, not a tuple or list: %s' % (type(retval), retval)
        return retval

    @property
    def historyRoles(self):
        retval = rolesForPermissionOn('View History', self.context)
        assert type(retval) in (tuple, list),\
          'retval is a %s, not a tuple or list: %s' % (type(retval), retval)
        return retval

provideAdapter(GSContentPagePrivacyContentProvider, provides=IContentProvider,
                name="groupserver.ContentPagePrivacy")
