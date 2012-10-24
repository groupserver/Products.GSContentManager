# coding=utf-8
import re
import zope
from interfaces import *
from zope.interface import implements
from zope.size.interfaces import ISized
from zope.component import adapts, createObject
from Products.XWFCore.XWFUtils import munge_date
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import interfaces

import logging
log = logging.getLogger('GSContentManager')


class GSContentPageHistoryContentProvider(object):
    """ Provides the history of a page """

    implements(IGSContentPageHistoryContentProvider)
    adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request
        self.pageHistory = None

    def update(self):
        self.__updated = True
        self.pageHistory = GSPageHistory(self.context,
          self.startId, self.endId)

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)

    #########################################
    # Non standard methods below this point #
    #########################################

    @property
    def history(self):
        return self.get_history()

    def get_history(self):
        """ Gets all history entries of the page """
        objects = []
        publishedItem = None
        items = self.pageHistory.get_versions()
        items.reverse()
        for item in items:
            authorInfo = createObject('groupserver.UserFromId',
              self.context, item.editor)
            editor = {
              'name': authorInfo.name,
              'id': authorInfo.id,
              'url': authorInfo.url,
              'anonymous': authorInfo.anonymous
            }
            d = munge_date(self.context, item.creationDate)
            entry = {'editor': editor,
                      'size': ISized(item).sizeForDisplay(),
                      'modified': '',
                      'id': item.id,
                      'date': d,
                      'published': item.published,
                      'changing': self.changedVersion == item.id,
                      'children': [],
                      }
            if ((not item.published) and (publishedItem is not None)):
                publishedItem['children'].append(entry)
            else:
                objects.append(entry)
                publishedItem = entry

        return objects


class GSPageHistory(object):

    histRE = re.compile('content_en_[0-9]{14}')

    def __init__(self, context, startId=None, endId=None):
        self.context = context

        self.__keys = None
        self.__startId = startId
        self.__endId = endId

    def get_published_revision(self):
        """ Get the currently published revision of the content

        ARGUMENTS
            None

        RETURNS
            An XML Template, representing the published revision of
            the content.

        SIDE EFFECTS
            None
        """
        assert hasattr(self.context, 'published_revision'),\
            '%s (%s) has no published_revision property' %\
             (self.context, self.context.absolute_url(0))
        pr = getattr(self.context, 'published_revision')

        assert hasattr(self.context, pr), 'No %s in %s (%s)' %\
             (pr, self.context, self.context.absolute_url(0))
        retval = IGSContentPageVersion(getattr(self.context, pr))

        assert retval
        return retval

    @property
    def published(self):
        return self.get_published_revision()

    def get_versions(self):
        """Get the versions of the document.

        ARGUMENTS
            None

        RETURNS
            A list of XML templates, ordered by creation date (newest
            last). Each template represents a version of the content.

        SIDE EFFECTS
            None
        """
        objectValueTypes = ('XML Template', 'Page Template')
        templates = self.context.objectValues(objectValueTypes)
        retval = [IGSContentPageVersion(t) for t in templates
                  if self.histRE.match(t.getId())]
        retval.sort(version_sorter)
        ids = [v.id for v in retval]

        if ((self.__startId is not None) and (self.__startId in ids)):
            retval = retval[ids.index(self.__startId):]
        if ((self.__endId is not None) and (self.__endId in ids)):
            retval = retval[:ids.index(self.__endId) + 1]

        assert type(retval) == list, u'Not a list'
        assert len(retval) > 0, u'List is empty'
        return retval

    def get_current_version(self):
        """Get most recently created version of the document content

        The current version is the version that was mostly recently
        created, rather than the one that is currently published. The
        latter is returned by "get_published_revision".

        ARGUMENTS
            None

        RETURNS
            An XML templates that represents the most recent version
            of the content.

        SIDE EFFECTS
            None
        """
        retval = self.get_versions()[-1]
        assert retval
        assert hasattr(retval, 'id')
        return retval

    @property
    def current(self):
        return self.get_current_version()

    # Mapping Methods below
    def keys(self):
        retval = [v.id for v in self.get_versions()]
        assert type(retval) == list
        return retval

    def values(self):
        return self.get_versions()

    def items(self):
        retval = [(v.id, v) for v in self.values()]
        assert type(retval) == list
        return retval

    def has_key(self, key):
        return key in self.keys()

    def __contains__(self, key):
        return key in self.keys()

    def get(self, key, default=None):
        if key in self:
            retval = [v for v in self.values() if v.id == key][0]
        else:
            retval = default
        return retval

    def clear(self):
        raise NotImplementedError

    def iterkeys(self):
        return iter(self.keys())

    def itervalues(self):
        return iter(self.values)

    def iteritems(self):
        return iter(self.items())

    def pop(self):
        raise NotImplementedError

    def popitem(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def __len__(self):
        return len(self.keys())

    def __getitem__(self, key):
        if key in self:
            retval = self.get(key)
        else:
            raise KeyError(key)
        assert retval is not None
        return retval

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        return self.iterkeys()


def version_sorter(a, b):
    assert a
    assert hasattr(a, 'creationDate')
    assert b
    assert hasattr(b, 'creationDate')
    retval = 1
    if a.creationDate < b.creationDate:
        retval = -1
    elif a.creationDate == b.creationDate:
        retval = 0
    assert retval in (-1, 0, 1)
    return retval

zope.component.provideAdapter(GSContentPageHistoryContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ContentPageHistory")
