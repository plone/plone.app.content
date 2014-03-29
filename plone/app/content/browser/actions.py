# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import queryMultiAdapter
from zope.interface import Interface


class DeleteConfirmationForm(form.Form):

    fields = field.Fields()
    template = ViewPageTemplateFile('templates/delete_confirmation.pt')

    @property
    def is_locked(self):
        locking_view = queryMultiAdapter(
            (self.context, self.request), name='plone_lock_info')

        return locking_view and locking_view.is_locked_for_current_user()

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


class IRenameForm(Interface):
    """ """


class RenameForm(form.Form):

    fields = field.Fields(IRenameForm)

    @button.buttonAndHandler(_(u'Delete'),
                             name='delete')
    def handle_delete(self, action):
        pass

    @button.buttonAndHandler(_(u'label_cancel', default=u'Cancel'),
                             name='cancel')
    def handle_cancel(self, action):
        pass
