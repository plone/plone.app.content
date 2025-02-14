from plone.base import PloneMessageFactory as _
from plone.base.utils import human_readable_size
from plone.base.utils import is_expired
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import field
from z3c.form import form
from zope.deprecation.deprecation import deprecate
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.schema import Datetime
from zope.schema.fieldproperty import FieldProperty

import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.browser.content_status_history import ContentStatusHistoryView",
    ContentStatusHistoryView="plone.app.layout:browser.content_status_history.ContentStatusHistoryView",
)


class IContentStatusHistoryDates(Interface):
    """Interface for the two dates on content status history view"""

    effective_date = Datetime(
        title=_("label_effective_date", default="Publishing Date"),
        description=_(
            "help_effective_date_content_status_history",
            default="The date when the item will be published. If no "
            "date is selected the item will be published immediately.",
        ),
        required=False,
    )

    expiration_date = Datetime(
        title=_("label_expiration_date", default="Expiration Date"),
        description=_(
            "help_expiration_date_content_status_history",
            default="The date when the item expires. This will automatically "
            "make the item invisible for others at the given date. "
            "If no date is chosen, it will never expire.",
        ),
        required=False,
    )


class ContentStatusHistoryDatesForm(form.Form):
    fields = field.Fields(IContentStatusHistoryDates)
    ignoreContext = True
    label = "Content status history dates"

    effective_date = FieldProperty(IContentStatusHistoryDates["effective_date"])
    expiration_date = FieldProperty(IContentStatusHistoryDates["expiration_date"])
