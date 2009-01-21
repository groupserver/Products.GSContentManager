# coding=utf-8
from Products.Five import BrowserView
from zope.component import adapts, createObject
from page_history import GSPageHistory
from interfaces import IGSContentPage

class GSPHistoryView(BrowserView):
    def __init__(self, folder, request):
        self.context = self.folder = folder
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', folder)
        self.__userInfo = None

        self.hist = GSPageHistory(folder)
        
    @property
    def title(self):
        return self.hist.published.title

    @property
    def showChange(self):
        uo = self.userInfo.user
        p = uo.has_permission('Manage properties', self.folder)
        retval = p != None
        assert type(retval) == bool, \
          'Returning %s, not bool.' % retval
        return retval

    @property
    def userInfo(self):
        if self.__userInfo == None:
            self.__userInfo = createObject('groupserver.LoggedInUser',
              self.folder)
        retval = self.__userInfo
        assert retval
        return retval

