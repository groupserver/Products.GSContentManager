# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 E-Democracy.org and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import unicode_literals
from zope.interface.interface import Interface
from zope.schema import (ASCIILine, Bool, Choice, Datetime, Dict, Text,
    TextLine)
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.contentprovider.interfaces import IContentProvider


class IGSContentPage(Interface):
    pass


class IGSDataTemplate(Interface):
    pass


class IGSContentManagerFolderMarker(Interface):
    pass


class IGSContentPageVersion(Interface):
    """ Schema for a content page """

    id = ASCIILine(title='Identifier',  # lint:ok
        description='The identifier of the version.',
        required=True)

    title = ASCIILine(title='Title',
        description='The title of the page, which will appear in '
          'the title bar of the browser.',
        required=True)

    content = Text(title='Content',
        description='The content of this page.',
        required=False)

    published = Bool(title='Publish',
        description='If you publish the change it will be shown '
          'to people by default.',
        required=True,
        default=True)

    editor = ASCIILine(title='Editor ID',
        description='The identifier of the user who last edited '
          'this Page',
        required=False,
        default='')

    parentVersion = ASCIILine(title='Parent Version ID',
        description='The identifier of the page version that this '
          'version was based on.',
        required=False,
        default='')

    creationDate = Datetime(title='Creation Date',
        description='The date that the version was created',
        required=False)


class IGSContentPageHistory(Interface):
    """Marker interface for the history of a page
    """


class IGSMangePages(Interface):
    pageId = ASCIILine(title='Page Identifier',
      description='The identifier for the new page. No spaces '
        'are allowed.',
      required=False)

    title = TextLine(title='Title',
      description='The title of the page. This will appear at'
        'the top of the page and in the title bar of the browser.',
      required=False)

    newPageId = ASCIILine(title='New Page Identifier',
      description='The identifier the page should have after it '
        'has been copied. No spaces are allowed.',
      required=False)

    copyDestination = ASCIILine(title='Destination',
      description='Where the page should be copied to.',
      required=False)

    renamedPageId = ASCIILine(title='New Page Identifier',
      description='The new identifier for the page. No spaces '
        'are allowed.',
      required=False)

    moveDestination = ASCIILine(title='Destination',
      description='Where the page should be moved to.',
      required=False)

anyone = SimpleTerm(
  'anyone', 'anyone',
  'Anyone, including those that are not logged in.')
members = SimpleTerm(
  'members', 'members',
  'Only logged in members.')
administrators = SimpleTerm(
  'administrators', 'administrators',
  'Only administrators.'
)

viewLevels = SimpleVocabulary([anyone, members, administrators])
changeLevels = SimpleVocabulary([members, administrators])


class IGSChangePagePrivacy(Interface):
    view = Choice(title='View the page',
      description='Which group of users can view the page.',
      required=True,
      vocabulary=viewLevels)

    change = Choice(title='Change the page',
      description='Which group of users can change the page.',
      required=True,
      vocabulary=changeLevels)


class IGSContentManagerContextMenuContentProvider(IContentProvider):
    """The content provider for the context menu"""

    pageTemplateFileName = Text(title="Page Template File Name",
      description='The name of the ZPT file that is used to render the '
        'menu.',
      required=False,
      default="browser/templates/profileContextMenu.pt")


class IGSPageTreeContentProvider(IContentProvider):
    """The content provider for the context menu"""

    treeIdPrefix = TextLine(title='Tree Identifier Prefix',
      description='The text that is appended to the start of all '
        'tree-node identifiers.',
      default='tree-'
    )


class IGSContentPageHistoryContentProvider(IContentProvider):
    """The content provider for the page history """

    pageTemplateFileName = Text(title="Page Template File Name",
      description='The name of the ZPT file that is used to render the '
        'history',
      required=False,
      default="browser/templates/page_history.pt")

    changedVersion = Text(title='Changed Version',
      description='The identifier of the version that is being '
        'changed',
      required=False)

    showChange = Bool(title='Show Changed',
        description='True if the "change" links are shown in the '
          'history.',
         default=False)

    startId = ASCIILine(title='Start Identifier',
      description='The identifier for the page at the start of '
        'the history range.',
        required=False,
        default=None)

    endId = ASCIILine(title='End Identifier',
      description='The identifier for the page at the end of '
        'the history range.',
        required=False,
        default=None)


class IGSContentManagerTabMenuContentProvider(IContentProvider):
    """The content provider for the tab menu"""

    pageTemplateFileName = Text(title="Page Template File Name",
      description='The name of the ZPT file that is used to render '
        'the menu.',
      required=False,
      default="browser/templates/tabmenu.pt")

    pages = Dict(title='Pages in the Profile',
      description='The pages that are in the context of the profile.')


class IGSContentPagePrivacyContentProvider(IContentProvider):
    """The content provider for the tab menu"""

    pageTemplateFileName = Text(title="Page Template File Name",
      description='The name of the ZPT file that is used to render '
        'the privacy.',
      required=False,
      default="browser/templates/privacy.pt")
