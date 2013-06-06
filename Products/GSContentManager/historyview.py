# coding=utf-8
from zope.cachedescriptors.property import Lazy
from gs.content.base import SitePage
from page_history import GSPageHistory


class GSPHistoryView(SitePage):
    def __init__(self, folder, request):
        super(GSPHistoryView, self).__init__(folder, request)
        self.folder = folder

    @Lazy
    def hist(self):
        retval = GSPageHistory(self.folder)
        return retval

    @property
    def title(self):
        return self.hist.published.title

    @property
    def showChange(self):
        uo = self.loggedInUserInfo.user
        p = uo.has_permission('Manage properties', self.folder)
        retval = p is not None
        assert type(retval) == bool, \
          'Returning %s, not bool.' % retval
        return retval

    @property
    def userInfo(self):
        return self.loggedInUser
