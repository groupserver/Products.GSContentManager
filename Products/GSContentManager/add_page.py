# coding=utf-8
'''Implementation of the Add Page form.
'''
try:
    from five.formlib.formbase import AddForm
except ImportError:
    from Products.Five.formlib.formbase import AddForm  # lint:ok
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import TextAreaWidget
from zope.app.apidoc.interface import getFieldsInOrder
from zope.schema import *
import interfaces
from page import GSContentPage


def wym_editor_widget(field, request):
    retval = TextAreaWidget(field, request)
    retval.cssClass = 'wymeditor'
    return retval


class AddPageForm(AddForm):
    label = u'Add Page'
    pageTemplateFileName = 'browser/templates/edit_page.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.interface = interface = getattr(interfaces, 'IGSContentPage')

        AddForm.__init__(self, context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', context)
        site_root = context.site_root()

        assert hasattr(site_root, 'GlobalConfiguration')

        self.form_fields = form.Fields(interface, render_context=True,
                                        omit_readonly=True)

        self.form_fields['content'].custom_widget = wym_editor_widget
        self.form_fields['content'].field.default = u'<p>Enter content '\
            u'here.</p>'

        self.mode = 'add'

    @property
    def id(self):
        return self.form_fields['id']

    @property
    def title(self):
        return self.form_fields['title']

    @property
    def description(self):
        return self.form_fields['description']

    @property
    def content(self):
        return self.form_fields['content']

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if
    #   necessary). I did not need to explicitly state that "Edit" is the
    #   label, but it helps with readability.
    @form.action(label=u'Add', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        return self.set_data(data)

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def set_data(self, data):
        assert self.context
        assert self.form_fields

        alteredFields = []
        for datum in getFieldsInOrder(self.interface):
            if datum[0] in data:
                if data[datum[0]] != getattr(self.context, datum[0]):
                    alteredFields.append(datum[0])

        # Create the content folder and object and apply changes.
        folder = GSContentPage(self.context, mode='add', id=data['id'])
        if folder.status['error']:
            retval = u'%s' % folder.status['msg']

        changed = form.applyChanges(folder, self.form_fields, data)

        # All good, so redirect to the edit page.
        if changed:
            url = '%s/edit_page.html' % folder.context.absolute_url(0)
            self.request.response.redirect(url)
            return
        else:
            retval = u'Problem creating page'

        assert retval
        assert type(retval) == unicode
        self.status = retval
