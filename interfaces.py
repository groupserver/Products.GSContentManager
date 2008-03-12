# coding=utf-8
"""Interfaces for the registration and password-reset pages."""
import re, pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary
from zope.contentprovider.interfaces import IContentProvider

class IGSContentPage(Interface):
    """ Schema for a content page """

    id = ASCIILine(title=u'Page ID',
        description=u'The unique ID of this page, which will be used '
          'in the page URL.',
        required=True)

    title = ASCIILine(title=u'Page title',
        description=u'The title of this page, which will appear in the '
          u'META title tag on the page.',
        required=True)

    description = ASCIILine(title=u'Page description',
        description=u'The description of this page, which will appear '
          u'in the META description tag on the page.',
        required=False,
        default='')
    
    hidden = Bool(title=u'Hidden',
        description=u'Whether the page is hidden from anonymous users '
          u'or not.',
        required=True,
        default=True)
    
    published_revision = ASCIILine(title=u'Published Revision',
        description=u'The published revision of the page.',
        required=False,
        default='content_en',
        readonly=True)
    
    content = Text(title=u'Page content',
        description=u'The content of this page.',
        required=True)
    
class IGSContentPageHistory(Interface):
    """Marker interface for the history of a page
    """
    
class IGSContentManagerContextMenuContentProvider(IContentProvider):
    """The content provider for the context menu"""
    
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '\
        u'menu.',
      required=False,
      default=u"browser/templates/profileContextMenu.pt")
      
    pages = Dict(title=u'Pages in the Profile',
      description=u'The pages that are in the context of the profile.')

class IGSContentPageHistoryContentProvider(IContentProvider):
    """The content provider for the page history """
    
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '
        u'history',
      required=False,
      default=u"browser/templates/page_history.pt")
      
    history = Dict(title=u'History entries for the page',
      description=u'The hisotory entries for this page.')
