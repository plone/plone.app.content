# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from z3c.form import form
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.schema import Datetime
from zope.schema.fieldproperty import FieldProperty


class IContentStatusHistoryDates(Interface):
    """ Interface for the two dates on content status history view
    """

    effective_date = Datetime(
        title=_(u"label_effective_date",
                default=u"Publishing Date"),
        description=_(
            u"help_effective_date",
            default=u"The date when the item will be published. If no "
                    u"date is selected the item will be published immediately."
        ),
        required=False)

    expiration_date = Datetime(
        title=_(u"label_expiration_date",
                default=u"Expiration Date"),
        description=_(
            u"help_expiration_date",
            default=u"The date when the item expires. This will automatically "
                    u"make the item invisible for others at the given date. "
                    u"If no date is chosen, it will never expire."
            ),
        required=False)


class ContentStatusHistoryDatesForm(form.Form):
    fields = field.Fields(IContentStatusHistoryDates)
    ignoreContext = True
    label = "Content status history dates"

    effective_date = FieldProperty(
        IContentStatusHistoryDates['effective_date']
    )
    expiration_date = FieldProperty(
        IContentStatusHistoryDates['expiration_date']
    )


class ContentStatusHistoryView(BrowserView):

    template = ViewPageTemplateFile('templates/content_status_history.pt')

    def __init__(self, context, request):
        super(ContentStatusHistoryView, self).__init__(context, request)

        self.dates_form = ContentStatusHistoryDatesForm(context, request)
        self.dates_form.updateWidgets()
        self.plone_utils = getToolByName(context, 'plone_utils')
        self.errors = {}

    def __call__(self, workflow_action=None, paths=[], comment="",
                 effective_date=None, expiration_date=None,
                 include_children=False, *args):

        data = self.dates_form.extractData()
        if self.request.get('form.widgets.effective_date-calendar', None) \
           and data:
            effective_date = data[0]['effective_date'].strftime(
                "%Y-%m-%d %H:%M"
            )

        if self.request.get('form.widgets.expiration_date-calendar', None) \
           and data:
            expiration_date = data[0]['expiration_date'].strftime(
                "%Y-%m-%d %H:%M"
            )

        if self.request.get('form.button.Cancel', None):
            return self.request.RESPONSE.redirect(
                "%s/view" % self.context.absolute_url())

        if self.request.get('form.submitted', None):
            self.validate(workflow_action=workflow_action, paths=paths)
            if self.errors:
                self.plone_utils.addPortalMessage(
                    _(u'Please correct the indicated errors.'), 'error')
                return self.template()

        if self.request.get('form.button.Publish', None):
            return self.context.restrictedTraverse('content_status_modify')(
                workflow_action=workflow_action,
                comment=comment,
                effective_date=effective_date,
                expiration_date=expiration_date)

        if self.request.get('form.button.FolderPublish', None):
            self.context.restrictedTraverse('folder_publish')(
                workflow_action=workflow_action,
                paths=paths,
                comment=comment,
                expiration_date=expiration_date,
                effective_date=effective_date,
                include_children=include_children)

        return self.template()

    def validate(self, workflow_action=None, paths=[]):
        if workflow_action is None:
            self.errors['workflow_action'] = _(
                u'You must select a publishing action.')

        if not paths:
            self.errors['paths'] = _(
                u'You must select content to change.')
            # If there are no paths, it's mostly a mistake
            # Set paths using orgi_paths, otherwise users are getting confused
            orig_paths = self.request.get('orig_paths')
            self.request.set('paths', orig_paths)
