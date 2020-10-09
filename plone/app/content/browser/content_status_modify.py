from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from DateTime import DateTime
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import transaction_note
from Products.Five import BrowserView
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter


class ContentStatusModifyView(BrowserView):
    """Handles the workflow transitions of objects.

    Former Controller Python Script "content_status_modify".

    [validators]
    validators = validate_content_status_modify

    [actions]
    action.failure=traverse_to:string:content_status_history
    action.success=redirect_to_action:string:view

    """

    def __call__(
        self,
        workflow_action=None,
        comment="",
        effective_date=None,
        expiration_date=None,
        *args,
    ):
        context = aq_inner(self.context)
        self.plone_utils = getToolByName(context, "plone_utils")
        # First check if the main argument is given.
        if not workflow_action:
            self.plone_utils.addPortalMessage(
                _("You must select a publishing action."), "error"
            )
            url = f"{context.absolute_url()}/content_status_history"
            return self.request.response.redirect(url)
        # If a workflow action was specified, there must be a plone.protect authenticator.
        CheckAuthenticator(self.request)

        # Check that the transition is valid.
        portal_workflow = getToolByName(context, "portal_workflow")
        transitions = portal_workflow.getTransitionsFor(context)
        transition_ids = [t["id"] for t in transitions]

        if (
            workflow_action in transition_ids
            and not effective_date
            and context.EffectiveDate() == "None"
        ):
            # TODO Check if effective date is really set
            effective_date = DateTime()

        # You can transition content but not have the permission to ModifyPortalContent.
        contentEditSuccess = 0
        try:
            self.editContent(context, effective_date, expiration_date)
            contentEditSuccess = 1
        except Unauthorized:
            pass

        # Create the note while we still have access to the original context
        note = "Changed status of %s at %s" % (
            context.title_or_id(),
            context.absolute_url(),
        )

        if workflow_action in transition_ids:
            # The action could result in a move or delete.
            # In that case we get a new context as answer.
            context = portal_workflow.doActionFor(
                context, workflow_action, comment=comment
            )
            if context is None:
                # the normal case
                context = aq_inner(self.context)

        # The object post-transition could now have ModifyPortalContent permission.
        if not contentEditSuccess:
            try:
                self.editContent(context, effective_date, expiration_date)
            except Unauthorized:
                pass

        transaction_note(note)

        # If this item is the default page in its parent, attempt to publish that
        # too. It may not be possible, of course
        if self.plone_utils.isDefaultPage(context):
            parent = aq_parent(context)
            try:
                parent_modify_view = getMultiAdapter(
                    (parent, self.request), name="content_status_modify"
                )
                parent_modify_view(
                    workflow_action,
                    comment,
                    effective_date=effective_date,
                    expiration_date=expiration_date,
                )
            except ConflictError:
                raise
            except Exception:
                pass

        self.plone_utils.addPortalMessage(_("Item state changed."))
        return self.request.response.redirect(context.absolute_url())

    def editContent(self, obj, effective, expiry):
        kwargs = {}
        # may contain the year
        # TODO what about plain datetime?
        if effective and (isinstance(effective, DateTime) or len(effective) > 5):
            kwargs["effective_date"] = effective
        # may contain the year
        if expiry and (isinstance(expiry, DateTime) or len(expiry) > 5):
            kwargs["expiration_date"] = expiry
        self.plone_utils.contentEdit(obj, **kwargs)
