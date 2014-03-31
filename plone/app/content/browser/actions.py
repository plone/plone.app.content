# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.protect.postonly import check as checkpost
from zExceptions import Unauthorized
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.widget import ComputedWidgetAttribute
from zope import schema
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent

import transaction


class ProtectedBaseForm(form.Form):
    """ Abstract CSRF protected base form.
    """

    # XXX: Is this really required?
    def protect(self):
        authenticator = getMultiAdapter(
            (self.context, self.request), name='authenticator')

        if not authenticator.verify():
            raise Unauthorized

        checkpost(self.request)

    @property
    def is_locked(self):
        locking_view = queryMultiAdapter(
            (self.context, self.request), name='plone_lock_info')

        return locking_view and locking_view.is_locked_for_current_user()


class DeleteConfirmationForm(ProtectedBaseForm):

    fields = field.Fields()
    template = ViewPageTemplateFile('templates/delete_confirmation.pt')
    enableCSRFProtection = True

    @property
    def items_to_delete(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        putils = getToolByName(self.context, 'plone_utils')
        results = catalog({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': putils.getUserFriendlyTypes(),
        })
        return len(results)

    @button.buttonAndHandler(_(u'Delete'), name='delete')
    def handle_delete(self, action):
        title = self.context.Title()
        parent = aq_parent(aq_inner(self.context))
        parent.manage_delObjects(ids=self.context.getId())
        IStatusMessage(self.request).add(
            _(u'${title} has been deleted.', mapping={u'title': title}))

        self.request.response.redirect(parent.absolute_url())

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='cancel')
    def handle_cancel(self, action):
        self.request.response.redirect(self.context.absolute_url())


def valid_id(self):
    # TODO: Do we need an validator here or use the same that's used in
    #       plone.app.dexterity.behaviors.id.IShortName
    return True


class IRenameForm(Interface):
    new_id = schema.ASCIILine(
        title=_(u'label_new_short_name', default=u'New Short Name'),
        description=_(u'help_short_name_url', default=
                      u'Short name is the part that shows up in the URL ' +
                      u'of the item.'),
        constraint=valid_id,
    )

    new_title = schema.TextLine(
        title=_(u'label_new_title', default=u'New Title'),
    )


default_new_id = ComputedWidgetAttribute(
    lambda form: form.context.getId(), field=IRenameForm['new_id'])

default_new_title = ComputedWidgetAttribute(
    lambda form: form.context.Title(), field=IRenameForm['new_title'])


class RenameForm(ProtectedBaseForm):

    fields = field.Fields(IRenameForm)
    template = ViewPageTemplateFile('templates/object_rename.pt')
    enableCSRFProtection = True
    ignoreContext = True

    label = _(u'heading_rename_item', default=u'Rename item')
    description = _(u'description_rename_item', default=
                    u'Each item has a Short Name and a Title, which you can ' +
                    u'change by entering the new details below.')

    @button.buttonAndHandler(_(u'Rename'), name='rename')
    def handle_rename(self, action):
        data, errors = self.extractData()
        if errors:
            return

        parent = aq_parent(aq_inner(self.context))
        sm = getSecurityManager()
        if not sm.checkPermission('Copy or Move', parent):
            raise Unauthorized(_(u'Permission denied to rename ${title}.',
                                 mapping={u'title': self.context.title}))

        oldid = self.context.getId()
        newid = data['new_id']

        # Requires cmf.ModifyPortalContent permission
        self.context.title = data['new_title']
        # Requires zope2.CopyOrMove permission
        parent.manage_renameObjects([oldid, ], [str(newid), ])

        transaction.savepoint(optimistic=True)
        notify(ObjectModifiedEvent(self.context))

        IStatusMessage(self.request).add(
            _(u"Renamed '${oldid}' to '${newid}'.", mapping={
                u'oldid': oldid, u'newid': newid}))

        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'label_cancel', default=u'Cancel'),
                             name='cancel')
    def handle_cancel(self, action):
        self.request.response.redirect(self.context.absolute_url())
