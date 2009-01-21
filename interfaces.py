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
      
    history = Dict(title=u'History entries for the page',
      description=u'The hisotory entries for this page.')

    showChange = Bool(title=u'Show Changed',
        description=u'True if the "change" links are shown in the '\
          u'history.',
         default=False)

