from AccessControl import Unauthorized
from AccessControl.Permissions import delete_objects
from plone.app.content.browser.contents import ContentsBaseAction
from plone.app.content.utils import get_recycle_bin_message
from plone.app.content.interfaces import IStructureAction
from plone.base import PloneMessageFactory as _
from plone.base.interfaces.recyclebin import IRecycleBin
from plone.locking.interfaces import ILockable
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer

import json


@implementer(IStructureAction)
class DeleteAction:
    template = ViewPageTemplateFile("templates/delete.pt")
    order = 4

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_options(self):
        return {
            "tooltip": translate(_("Delete"), context=self.request),
            "id": "delete",
            "icon": "plone-delete",
            "context": "danger",
            "url": self.context.absolute_url() + "/@@fc-delete",
            "form": {
                "title": translate(_("Delete selected items"), context=self.request),
                "submitText": translate(_("Yes"), context=self.request),
                "submitContext": "danger",
                "template": self.template(),
                "closeText": translate(_("No"), context=self.request),
                "dataUrl": self.context.absolute_url() + "/@@fc-delete",
            },
        }


class DeleteActionView(ContentsBaseAction):
    required_obj_permission = delete_objects
    failure_msg = _("Failed to delete items")

    @property
    def success_msg(self):
        """Dynamic success message that includes recycle bin information."""
        # Check if recycle bin is enabled
        recycle_bin = queryUtility(IRecycleBin)
        recycling_enabled = recycle_bin.is_enabled() if recycle_bin else False

        if not recycling_enabled:
            return _("Successfully deleted items")

        # Get retention period from registry
        registry = queryUtility(IRegistry)
        retention_period = registry["recyclebin-controlpanel.retention_period"]

        return get_recycle_bin_message(retention_period=retention_period)

    def __call__(self):
        if self.request.form.get("render") == "yes":
            confirm_view = getMultiAdapter(
                (getSite(), self.request), name="delete_confirmation_info"
            )
            selection = self.get_selection()
            catalog = getToolByName(self.context, "portal_catalog")
            brains = catalog(UID=selection, show_inactive=True)
            items = [i.getObject() for i in brains]
            self.request.response.setHeader(
                "Content-Type", "application/json; charset=utf-8"
            )
            return json.dumps({"html": confirm_view(items)})
        else:
            return super().__call__()

    def action(self, obj):
        parent = obj.aq_inner.aq_parent
        title = self.objectTitle(obj)

        try:
            lock_info = obj.restrictedTraverse("@@plone_lock_info")
        except AttributeError:
            lock_info = None
        if lock_info is not None:
            if lock_info.is_locked_for_current_user():
                self.errors.append(
                    _(
                        "${title} is locked and cannot be deleted.",
                        mapping={"title": title},
                    )
                )
                return
            elif lock_info.is_locked():
                # unlock object as it is locked by current user
                ILockable(obj).unlock()

        try:
            parent.manage_delObjects(obj.getId())
        except Unauthorized:
            self.errors.append(
                _(
                    "You are not authorized to delete ${title}.",
                    mapping={"title": self.objectTitle(self.dest)},
                )
            )
