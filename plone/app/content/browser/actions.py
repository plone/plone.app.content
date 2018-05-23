# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.CopySupport import CopyError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.widget import ComputedWidgetAttribute
from zExceptions import Unauthorized
from zope import schema
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent

import six
import transaction


class LockingBase(BrowserView):

    @property
    def is_locked(self):
        locking_view = queryMultiAdapter(
            (self.context, self.request), name='plone_lock_info')

        return locking_view and locking_view.is_locked_for_current_user()


class DeleteConfirmationForm(form.Form, LockingBase):

    fields = field.Fields()
    template = ViewPageTemplateFile('templates/delete_confirmation.pt')
    enableCSRFProtection = True

    def view_url(self):
        ''' Facade to the homonymous plone_context_state method
        '''
        context_state = getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )
        return context_state.view_url()

    def more_info(self):
        adapter = queryMultiAdapter(
            (self.context, self.request), name='delete_confirmation_info')
        if adapter:
            return adapter()
        return ""

    @property
    def items_to_delete(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        putils = getToolByName(self.context, 'plone_utils')
        results = catalog({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': putils.getUserFriendlyTypes(),
        })
        return len(results)

    @button.buttonAndHandler(_(u'Delete'), name='Delete')
    def handle_delete(self, action):
        title = safe_unicode(self.context.Title())
        parent = aq_parent(aq_inner(self.context))

        # has the context object been acquired from a place it should not have
        # been?
        if self.context.aq_chain == self.context.aq_inner.aq_chain:
            parent.manage_delObjects(self.context.getId(), self.request)
            IStatusMessage(self.request).add(
                _(u'${title} has been deleted.', mapping={u'title': title}))
        else:
            IStatusMessage(self.request).add(
                _(u'"${title}" has already been deleted',
                  mapping={u'title': title})
            )

        self.request.response.redirect(parent.absolute_url())

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='Cancel')
    def handle_cancel(self, action):
        target = self.view_url()
        return self.request.response.redirect(target)


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


class RenameForm(form.Form):

    fields = field.Fields(IRenameForm)
    template = ViewPageTemplateFile('templates/object_rename.pt')
    enableCSRFProtection = True
    ignoreContext = True

    label = _(u'heading_rename_item', default=u'Rename item')
    description = _(u'description_rename_item', default=
                    u'Each item has a Short Name and a Title, which you can ' +
                    u'change by entering the new details below.')

    def view_url(self):
        context_state = getMultiAdapter(
            (self.context, self.request), name='plone_context_state')
        return context_state.view_url()

    @button.buttonAndHandler(_(u'Rename'), name='Rename')
    def handle_rename(self, action):
        data, errors = self.extractData()
        if errors:
            return

        parent = aq_parent(aq_inner(self.context))
        sm = getSecurityManager()
        if not sm.checkPermission('Copy or Move', parent):
            raise Unauthorized(_(u'Permission denied to rename ${title}.',
                                 mapping={u'title': self.context.title}))

        # Requires cmf.ModifyPortalContent permission
        self.context.title = data['new_title']

        oldid = self.context.getId()
        newid = data['new_id']
        if oldid != newid:
            newid = INameChooser(parent).chooseName(newid, self.context)

            # Requires zope2.CopyOrMove permission

            # manage_renameObjects fires 3 events:
            # 1. ObjectWillBeMovedEvent before anything happens
            # 2. ObjectMovedEvent directly after rename
            # 3. zope.container.contained.notifyContainerModified directly after 2
            # for 2+3 there are subscribers in Products.CMFDynamicViewFTI
            # responsible to change (2) or unset (3) the default_page.

            parent.manage_renameObjects([oldid, ], [str(newid), ])
        else:
            # Object is not reindex if manage_renameObjects is not called
            self.context.reindexObject()

        transaction.savepoint(optimistic=True)
        notify(ObjectModifiedEvent(self.context))

        IStatusMessage(self.request).add(
            _(u"Renamed '${oldid}' to '${newid}'.", mapping={
                u'oldid': oldid, u'newid': newid}))

        self.request.response.redirect(self.view_url())

    @button.buttonAndHandler(_(u'label_cancel', default=u'Cancel'),
                             name='Cancel')
    def handle_cancel(self, action):
        self.request.response.redirect(self.view_url())


class ObjectCutView(LockingBase):

    @property
    def title(self):
        if six.PY2:
            return self.context.Title().decode('utf8')
        return self.context.Title()

    @property
    def parent(self):
        return aq_parent(aq_inner(self.context))

    @property
    def canonical_object_url(self):
        context_state = getMultiAdapter(
            (self.context, self.request), name='plone_context_state')
        return context_state.canonical_object_url()

    @property
    def view_url(self):
        context_state = getMultiAdapter(
            (self.context, self.request), name='plone_context_state')
        return context_state.view_url()

    def do_redirect(self, url, message=None, message_type='info',
                    raise_exception=None):
        if message is not None:
            IStatusMessage(self.request).add(message, type=message_type)

        if raise_exception is None:
            return self.request.response.redirect(url)
        raise raise_exception

    def do_action(self):
        if self.is_locked:
            return self.do_redirect(self.view_url,
                                    _(u'${title} is locked and cannot be cut.',
                                        mapping={'title': self.title, }))

        try:
            self.parent.manage_cutObjects(self.context.getId(), self.request)
        except CopyError:
            return self.do_redirect(self.view_url,
                                    _(u'${title} is not moveable.',
                                        mapping={'title': self.title}))

        return self.do_redirect(
            self.view_url,
            _(u'${title} cut.', mapping={'title': self.title}),
            'info'
        )

    def __call__(self):
        authenticator = getMultiAdapter(
            (self.context, self.request), name='authenticator')

        if not authenticator.verify():
            raise Unauthorized

        return self.do_action()


class ObjectCopyView(ObjectCutView):

    def do_action(self):
        try:
            self.parent.manage_copyObjects(self.context.getId(), self.request)
        except CopyError:
            return self.do_redirect(self.view_url,
                                    _(u'${title} is not copyable.',
                                        mapping={'title': self.title}))

        return self.do_redirect(self.view_url,
                                _(u'${title} copied.',
                                    mapping={'title': self.title}))


class ObjectDeleteView(ObjectCutView):

    def do_action(self):
        form = DeleteConfirmationForm(self.context, self.request)
        form.update()

        button = form.buttons['Delete']
        # delete by clicking the form button in delete_confirmation
        form.handlers.getHandler(button)(form, button)


class ObjectPasteView(ObjectCutView):

    def do_action(self):
        if not self.context.cb_dataValid():
            return self.do_redirect(
                self.canonical_object_url,
                _(u'Copy or cut one or more items to paste.'),
                'error'
            )
        try:
            self.context.manage_pasteObjects(self.request['__cp'])
        except ConflictError:
            raise
        except Unauthorized as e:
            self.do_redirect(
                self.canonical_object_url,
                _(u'You are not authorized to paste here.'),
                e
            )
        except CopyError as e:
            error_string = str(e)
            if 'Item Not Found' in error_string:
                return self.do_redirect(
                    self.canonical_object_url,
                    _(u'The item you are trying to paste could not be found. '
                      u'It may have been moved or deleted after you copied or '
                      u'cut it.'),
                    'error',
                )
        except Exception as e:
            if '__cp' in self.request:
                self.do_redirect(self.canonical_object_url, e, 'error', e)

        return self.do_redirect(self.canonical_object_url,
                                _(u'Item(s) pasted.'))
