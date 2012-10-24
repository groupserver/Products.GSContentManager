# coding=utf-8
from zope.component import createObject
from interfaces import *
from zope.interface import implements
from gs.content.base import SitePage
from changeprivacy import Permissions
from page_history import GSPageHistory


class GSContentPage(SitePage):
    """The view of a version-controlled content page."""

    implements(IGSContentPage)

    CONTENT_TEMPLATE = 'content_en'
    initial_content_file = 'content.html'

    def __init__(self, context, request):
        super(GSContentPage, self).__init__(context, request)
        self.pageHistory = GSPageHistory(context)
        self.__userInfo = self.__showChangeLink = None

    @property
    def userInfo(self):
        return self.loggedInUserInfo

    @property
    def showChangeLink(self):
        '''The Change link is a bit special. It is *only* shown to the
            anonymous user iff members can edit the page. This is
            because the person viewing the page can easily acquire
            the privilages required to edit the page.'''
        if self.__showChangeLink is None:
            perms = Permissions(self.context)
            memberChange = perms.get_change() == 'members'
            anon = self.userInfo.anonymous
            self.__showChangeLink = memberChange and anon
        assert type(self.__showChangeLink) == bool
        return self.__showChangeLink

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
            vid = self.request.form.get('form.version', retval.id)
            try:
                retval = self.pageHistory[vid]
            except KeyError:
                pass  # --=mpj17=-- Because we have already set retval
        assert retval, 'Return value not set'
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


class Page(object):

    def __init__(self, folder):
        self.context = self.folder = folder
        self.pageHistory = GSPageHistory(folder)

    @property
    def version(self):
        retval = self.pageHistory.published
        assert retval
        return retval

    @property
    def content(self):
        '''Gets the content from the requested version of the page.
        '''
        retval = self.version.content
        assert type(retval) in (str, unicode)
        return retval

    @property
    def id(self):
        '''The ID of the page is the ID of the folder that contains
        the page.
        '''
        return self.folder.id

    @property
    def name(self):
        retval = self.version.title
        assert type(retval) in (str, unicode)
        return retval

    @property
    def hidden(self):
        '''Returns the hidden value of the *entire* folder, not the
        version.
        '''
        retval = self.folder.hidden
        assert type(retval) == bool
        return retval

    @property
    def editor(self):
        '''Returns the name of the last editor.
        '''
        uid = self.version.editor
        retval = createObject('groupserver.UserFromId', self.context, uid)
        return retval

    @property
    def date(self):
        retval = self.version.creationDate
        return retval

    @property
    def url(self):
        return self.folder.absolute_url()
