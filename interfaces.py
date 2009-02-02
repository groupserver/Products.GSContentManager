# coding=utf-8
"""Interfaces for the registration and password-reset pages."""
import re, pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary
from zope.contentprovider.interfaces import IContentProvider

class IGSContentPage(Interface):
    pass
    
class IGSDataTemplate(Interface):
    pass

class IGSContentManagerFolderMarker(Interface):
    pass

class IGSContentPageVersion(Interface):
    """ Schema for a content page """

    id = ASCIILine(title=u'Identifier',
        description=u'The identifier of the version.',
        required=True)

    title = ASCIILine(title=u'Title',
        description=u'The title of the page, which will appear in '
          u'the title bar of the browser.',
        required=True)
    
    content = Text(title=u'Content',
        description=u'The content of this page.',
        required=False)

    published = Bool(title=u'Publish',
        description=u'If you publish the change it will be shown '
          u'to people by default.',
        required=True,
        default=True)
        
    editor = ASCIILine(title=u'Editor ID',
        description=u'The identifier of the user who last edited '
          u'this Page',
        required=False,
        default='')
        
    parentVersion = ASCIILine(title=u'Parent Version ID',
        description=u'The identifier of the page version that this '
          u'version was based on.',
        required=False,
        default='')
        
    creationDate = Datetime(title=u'Creation Date',
        description=u'The date that the version was created',
        required=False)

class IGSContentPageHistory(Interface):
    """Marker interface for the history of a page
    """

class IGSMangePages(Interface):
    pageId = ASCIILine(title=u'Page Identifier',
      description=u'The identifier for the new page. No spaces '\
        u'are allowed.')
    
    title = TextLine(title=u'Title',
      description=u'The title of the page. This will appear at'\
        u'the top of the page and in the title bar of the browser.')
    
    newPageId = ASCIILine(title=u'New Page Identifier',
      description=u'The identifier the page should have after it '\
        u'has been copied. No spaces are allowed.')

    copyDestination = ASCIILine(title=u'Destination',
      description=u'Where the page should be copied to.')

    renamedPageId = ASCIILine(title=u'New Page Identifier',
      description=u'The new identifier for the page. No spaces '\
        u'are allowed.')

    moveDestination = ASCIILine(title=u'Destination',
      description=u'Where the page should be moved to.')

class IGSContentManagerContextMenuContentProvider(IContentProvider):
    """The content provider for the context menu"""
    
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '\
        u'menu.',
      required=False,
      default=u"browser/templates/profileContextMenu.pt")
      
class IGSContentPageHistoryContentProvider(IContentProvider):
    """The content provider for the page history """
    
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '
        u'history',
      required=False,
      default=u"browser/templates/page_history.pt")

    changedVersion = Text(title=u'Changed Version',
      description=u'The identifier of the version that is being '\
        u'changed',
      required=False)

    showChange = Bool(title=u'Show Changed',
        description=u'True if the "change" links are shown in the '\
          u'history.',
         default=False)

    startId = ASCIILine(title=u'Start Identifier',
      description=u'The identifier for the page at the start of '\
        u'the history range.',
        required=False,
        default=None)
        
    endId = ASCIILine(title=u'End Identifier',
      description=u'The identifier for the page at the end of '\
        u'the history range.',
        required=False,
        default=None)

class IGSContentManagerTabMenuContentProvider(IContentProvider):
    """The content provider for the tab menu"""
    
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render '\
        u'the menu.',
      required=False,
      default=u"browser/templates/tabmenu.pt")
      
    pages = Dict(title=u'Pages in the Profile',
      description=u'The pages that are in the context of the profile.')

class IGSContentPagePrivacyContentProvider(IContentProvider):
    """The content provider for the tab menu"""
    
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render '\
        u'the privacy.',
      required=False,
      default=u"browser/templates/privacy.pt")

