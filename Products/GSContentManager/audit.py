# coding=utf-8
"""The audit-trails component for page editiong

CONSTANTS
    SUBSYSTEM: 'groupserver.PageEditor' (*Must* be the same as the
        factory named in the ZCML configuration.)
    UNKNOWN:          '0' (*String*)
    EDIT_CONTENT:     '1' (*String*)
    EDIT_FIELD        '2' (*String*)
    RENAME_PAGE       '3' (*String*)
    CHANGE_PRIVACY    '4' (*String*)
"""
from pytz import UTC
from datetime import datetime
from base64 import b64decode
from zope.component import createObject
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, \
  AuditQuery, event_id_from_data
from Products.XWFCore.XWFUtils import munge_date

# Create a logger for this audit-trail component that dumps
SUBSYSTEM = 'groupserver.PageEditor'
import logging
log = logging.getLogger(SUBSYSTEM)
UNKNOWN = '0'  # Unknown is always "0"
EDIT_CONTENT = '1'
EDIT_FIELD = '2'
RENAME_PAGE = '3'
CHANGE_PRIVACY = '4'
EDIT_ATTRIBUTE = '5'


class EditPageAuditEventFactory(object):
    """A Factory for edit page events
    """
    implements(IFactory)

    title = u'ABEL YAPA Enrol Audit Event Factory'
    description = u'Creates a GroupServer audit event'

    def __call__(self, context, event_id, code, date, userInfo,
        instanceUserInfo, siteInfo, groupInfo=None, instanceDatum='',
        supplementaryDatum='', subsystem=''):
        """Create an event

        DESCRIPTION
            The factory is called to create event instances. It
            expects all the arguments that are required to create an
            event instance, though it ignores some. The arguments to
            this method *must* be the same for *all* event
            factories, no matter the subsystem, and the argument
            names *must* match the fields returned by the
            getter-methods of the audit trail query.

        ARGUMENTS
            context
                The context used to create the event.

            event_id
                The identifier for the event.

            code
                The code used to determine the event that is
                instantiated.

            date
                The date the event occurred.

            userInfo
                The user who caused the event. Always set.

            instanceUserInfo
                The user who had an event occurred to them.

            siteInfo
                The site where the event occurred. Always set.

            groupInfo
                The group where the event occurred. Can be None.

            instanceDatum
                Data about the event. Can be ''.

            supplementaryDatum
                More data about the event. Can be ''.

            subsystem
                The subsystem (should be this one).
        RETURNS
            An event, that conforms to the IAuditEvent interface.

        SIDE EFFECTS
            None
        """
        assert subsystem == SUBSYSTEM, 'Subsystems do not match'

        # The process of picking the class used to create an event
        #   not a pretty one: use the code in a big if-statement.
        #   Not all data-items are passed to the constructors of
        #   the classes that represent the events: they do not need
        #   the code or subsystem, for example.
        if (code == EDIT_CONTENT):
            event = EditContentEvent(context, event_id, date,
              userInfo, siteInfo, instanceDatum, supplementaryDatum)
        if (code == CHANGE_PRIVACY):
            event = ChangePrivacyEvent(context, event_id, date,
              userInfo, siteInfo, instanceDatum, supplementaryDatum)
        else:
            # If we get something odd, create a basic event with all
            #  the data we have. All call methods for audit-event
            #  factories will end in this call.
            event = BasicAuditEvent(context, event_id, UNKNOWN, date,
              userInfo, None, siteInfo, None,
              instanceDatum, supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


class EditContentEvent(BasicAuditEvent):
    '''An audit-trail event representing an edit to the page content

    DESCRIPTION
        A edit content event is generated when someone edits the
        content of a page that is managed the GroupServer Content
        Management subsystem.
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, siteInfo, instanceDatum,
                    supplementaryDatum):
        """Create an edit-content event

        ARGUMENTS
            Most of the arguments are the same as for the factory,
            except subsystem and code are skipped.

            userInfo
                The person who changed the page.

            siteInfo
                The site that contains the page.

            instanceDatum
                The url, title, old version identifier, and new
                version identifier. All base-64 encoded and separated
                by commas.

            supplementaryDatum
                A comparison of the two versions, in a unified-diff
                format and HTML table. Each comparison is base-64
                encoded and separated by commas.

        SIDE EFFECTS
            None
        """
        BasicAuditEvent.__init__(self, context, id,
          EDIT_CONTENT, d, userInfo, None,
          siteInfo, None, instanceDatum, supplementaryDatum,
          SUBSYSTEM)

    def __str__(self):
        """Display the event as a string, in such a way that it
        will be useful for the standard Python log.
        """
        url, title, oVid, nVid = [b64decode(d)
                                  for d in self.instanceDatum.split(',')]
        uDiff, htmlDiff = [b64decode(d)
                           for d in self.supplementaryDatum.split(',')]

        retval = u'%s (%s) changed the content of %s (%s) on '\
          u'%s (%s)\n%s' %\
          (self.userInfo.name, self.userInfo.id, title, url,
           self.siteInfo.name, self.siteInfo.id, uDiff)
        return retval

    @property
    def xhtml(self):
        """Display the event as string, with XHTML markup, in such
        a way that it will be useful for the Web view of audit
        trails.
        """
        cssClass = u'audit-event groupserver-page-edit-event-%s' %\
          self.code
        url, title, oVid, nVid = [b64decode(d)
                                  for d in self.instanceDatum.split(',')]
        uDiff, htmlDiff = [b64decode(d)
                           for d in self.supplementaryDatum.split(',')]

        retval = u'<div class="%s"><p>Edited content of '\
          u'<a href="%s">%s</a></p> %s <p>(%s)</p></span>' % \
          (cssClass, url, title, htmlDiff,
           munge_date(self.context, self.date))

        return retval


class EditAttributeEvent(BasicAuditEvent):
    '''An audit-trail event representing an edit to the page content

    DESCRIPTION
        A edit content event is generated when someone edits the
        content of a page that is managed the GroupServer Content
        Management subsystem.
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, siteInfo, instanceDatum,
                supplementaryDatum):
        """Create an edit-atribute event

        ARGUMENTS
            Most of the arguments are the same as for the factory,
            except subsystem and code are skipped.

            userInfo
                The person who changed the page.

            instanceDatum
                The URL of the page

            supplementaryDatum
                The title of the page.

        SIDE EFFECTS
            Creates and enrolment query instance, so it can find out
            about the offering.
        """
        BasicAuditEvent.__init__(self, context, id,
          EDIT_ATTRIBUTE, d, userInfo, None,
          siteInfo, None, instanceDatum, supplementaryDatum,
          SUBSYSTEM)

    def __str__(self):
        """Display the event as a string, in such a way that it
        will be useful for the standard Python log.
        """
        retval = u'%s (%s) changed the attribute of %s (%s) on %s (%s)' %\
          (self.userInfo.name, self.userInfo.id,
           self.supplementaryDatum, self.instanceDatum,
           self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        """Display the event as string, with XHTML markup, in such
        a way that it will be useful for the Web view of audit
        trails.
        """
        cssClass = u'audit-event groupserver-page-edit-event-%s' % self.code
        retval = u'<span class="%s">Edited attributes of '\
            u'<a href="%s">%s</a> (%s)</span>' % \
          (cssClass, self.instanceDatum, self.supplementaryDatum,
           munge_date(self.context, self.date))

        return retval


class RenamePageEvent(BasicAuditEvent):
    '''An audit-trail event representing renaming a page

    DESCRIPTION
        A rename-page event is generated when someone renames a
        page, changing its URL
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, siteInfo, instanceDatum,
                supplementaryDatum):
        """Create an edit-atribute event

        ARGUMENTS
            Most of the arguments are the same as for the factory,
            except subsystem and code are skipped.

            userInfo
                The person who changed the page.

            instanceDatum
                The original URL

            supplementaryDatum
                The new URL

        SIDE EFFECTS
            Creates and enrolment query instance, so it can find out
            about the offering.
        """
        BasicAuditEvent.__init__(self, context, id, RENAME_PAGE, d, userInfo,
                                    None, siteInfo, None, instanceDatum,
                                    supplementaryDatum, SUBSYSTEM)

    def __str__(self):
        """Display the event as a string, in such a way that it
        will be useful for the standard Python log.
        """
        retval = u'%s (%s) changed the URL of <%s> to <%s> on %s (%s)' %\
          (self.userInfo.name, self.userInfo.id,
           self.instanceDatum, self.supplementaryDatum,
           self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        """Display the event as string, with XHTML markup, in such
        a way that it will be useful for the Web view of audit
        trails.
        """
        cssClass = u'audit-event groupserver-page-edit-event-%s' % self.code
        retval = u'<span class="%s">Changed URL of '\
          u'<a href="%s"><code>%s</code></a> to '\
          u'<a href="%s"><code>%s</code></a></span>' % \
          (cssClass, self.instanceDatum, self.instanceDatum,
           self.supplementaryDatum, self.supplementaryDatum,
           munge_date(self.context, self.date))
        assert retval
        return retval


class ChangePrivacyEvent(BasicAuditEvent):
    '''An audit-trail event representing a change to the page privacy    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, siteInfo, instanceDatum,
                    supplementaryDatum):
        BasicAuditEvent.__init__(self, context, id, CHANGE_PRIVACY, d,
                userInfo, None, siteInfo, None, instanceDatum,
                supplementaryDatum, SUBSYSTEM)

    def __str__(self):
        retval = u'stuff'
        return retval

    @property
    def xhtml(self):
        retval = u'<p>stuff</p>'

        return retval


class PageEditAuditor(object):
    """An Auditor for Page Editor

    DESCRIPTION
        An auditor (sometimes called an auditer) creates an audit
        trail for a specific subsystem. In this case enrolment. The
        work of creating the actual events is carried out by the
        audit-event factory
    """
    def __init__(self, page):
        """Create an edit auditor.

        DESCRIPTION
            The constructor for an auditor is passed all the data
            that will be the same for the events that are created
            during one use of the auditor by a Zope 3 page-view.

        ARGUMENTS
            "page"    A IGSContentFolder representing the page being
                      edited.

        SIDE EFFECTS
            The page is set to the page that is passed in, and used
            as the context for the auditor.

            The user (who is acting on the page) is set after
            determining the logged-in user, using the page as the
            context.

            The site that all this is occurring on is set, after
            being determined by a similar mechanism to the user.

            A page-edit audit event factory is instantiated.
        """
        self.page = page
        self.userInfo = createObject('groupserver.LoggedInUser', page)
        self.siteInfo = createObject('groupserver.SiteInfo', page)

        self.queries = AuditQuery()

        self.factory = EditPageAuditEventFactory()

    def info(self, code, instanceDatum='', supplementaryDatum=''):
        """Log an info event to the audit trail.

        DESCRIPTION
            This method logs an event to the audit trail. It is
            named after the equivalent method in the standard Python
            logger, which it also writes to.

        ARGUMENTS
            "code"    The code that identifies the event that is
                      logged. Sometimes this is enough.
            "instanceDatum" The data to write as the instance datum
                      for the event. Defaults to an empty string.
                      (See below.)
            "supplementaryDatum" The data to write as the
                    supplementary datum for the event. Defaults to
                    an empty string. (See below.)

            If the instance datum *and* the supplementary datum are
            set to empty strings then they are set to the page URL
            and page title respectively.

        SIDE EFFECTS
            * Creates an ID for the new event,
            * Writes the instantiated event to the audit-table, and
            * Writes the event to the standard Python log.

        RETURNS
            None
        """
        d = datetime.now(UTC)
        if ((not instanceDatum) and (not supplementaryDatum)):
            instanceDatum = self.page.absolute_url(0)
            supplementaryDatum = self.page.title_or_id()
        eventId = event_id_from_data(self.userInfo, self.userInfo,
          self.siteInfo, code, instanceDatum, supplementaryDatum)

        e = self.factory(self.page, eventId, code, d,
          self.userInfo, None, self.siteInfo, None,
          instanceDatum, supplementaryDatum, SUBSYSTEM)
        self.queries.store(e)
        log.info(e)
