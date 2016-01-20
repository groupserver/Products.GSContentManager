Changelog
=========

3.1.1 (2016-01-20)
------------------

* Following the update to `gs.content.js.wymeditor`_
* Naming the reStructuredText files as such

3.1.0 (2014-06-13)
------------------

* Allowing the page-title to be Unicode, rather than ASCII
* Following `gs.content.form.base`_
* Adding a ``</div>`` to a ``<div/>``
* Fixing Unicode errors

.. _gs.content.form.base:
   https://github.com/groupserver/gs.content.form.base

3.0.0 (2013-11-19)
------------------

* Switching to the tabs supplied by Twitter Bootstrap, closing
  `Bug 3866`_
* Fixing some Unicode errors
* Following the WYMeditor code to `gs.content.js.wymeditor`_

.. _Bug 3866: https://redmine.iopen.net/issues/3866
.. _gs.content.js.wymeditor:
   https://github.com/groupserver/gs.content.js.wymeditor

2.4.8 (2013-09-24)
------------------

* Removing the obtrusive *Login* link

2.4.7 (2013-06-06)
------------------

* Fixing a JavaScript error
* Fixing an error with the *Change* page
* Explicitly specifying a page-layout with a context-menu

2.4.6 (2012-10-24)
------------------

* Fixing a miss-matched tag
* Importing the correct ``SitePage`` class
* Cleaning up the code

2.4.5 (2012-06-22)
------------------

* Updating SQLAlchemy_

.. _SQLAlchemy: http://www.sqlalchemy.org/

2.4.2 (2012-02-07)
------------------

* Changes to allow ``wsgi`` to work

2.4.1 (2011-03-10)
------------------

* Linking to the *Change* page for Anonymous
* Using a better URL for the *View* link from the *History* list

2.4.0 (2010-12-09)
------------------

* Using ``jQuery.UI`` tabs
* Using the new form-message content provider

2.3.2 (2010-10-07)
------------------

* Following the definition of the radio-button widget to
  ``gs.content.form`` from ``Products.GSGroup``

2.3.1 (2010-08-19)
------------------

* Updating the product metadata

2.3.0 (2010-07-23)
------------------

* Following the changes to ``zope.formlib``
* Removing deprecated code
* Updating the product metadata

2.2.1 (2009-10-08)
------------------

* Turning the product into an egg
* Fixing a Unicode error

2.2.0 (2009-08-31)
------------------

* Making the *WYMeditor* look like GroupServer
* Upgrading to WYMeditor 0.5rc1

2.1.0 (2009-06-26)
------------------

* Adding a *Privacy* page

2.0.2 (2009-05-06)
------------------

* Outputting ``text/html``, rather than ``text/xml``
* Fixing the JavaScript on the *Edit* page

2.0.1 (2009-04-03)
------------------

* Dealing with Googlebot

2.0.0 (2009-02-09)
------------------

* Handle edits being made by Anonymous
* Adding the *Manage pages* page
* Adding a page-tree
* Adding adding of pages
* Adding disclosure buttons to the *History* list
* Increasing the height of the *Content* entry
* Loading the new version after committing the change
* Switching to *Page templates* from *XML templates* for the
  data-store
* Moving the CSS into the global style-sheet
* Dealing with roles that contain white-space characters
* Fixing Unicode errors


1.2.0 (2008-12-19)
------------------

* Adding new *History* features
* Moving the metadata editing from the page editor to a new
  metadata editor
* Updating the auditor


1.1.0 (2008-06-11)
------------------

* Publishing a revision so it now only marks a revision as
  published, rather than modifying or creating a new revision

1.0.0 (2008-03-17)
------------------

Initial version. Prior to the creation of this product content
was never editable from the GroupServer user-interface.

..  LocalWords:  Changelog
