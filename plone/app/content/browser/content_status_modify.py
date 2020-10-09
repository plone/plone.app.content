from AccessControl import Unauthorized
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import transaction_note
from Products.Five import BrowserView
from ZODB.POSException import ConflictError


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
        *args
    ):
        context = self.context
        plone_utils = getToolByName(context, "plone_utils")
        contentEditSuccess = 0
        portal_factory = getattr(context, "portal_factory", None)
        if portal_factory is not None:
            new_context = context.portal_factory.doCreate(context)
        else:
            new_context = context
        portal_workflow = new_context.portal_workflow
        transitions = portal_workflow.getTransitionsFor(new_context)
        transition_ids = [t["id"] for t in transitions]

        if (
            workflow_action in transition_ids
            and not effective_date
            and context.EffectiveDate() == "None"
        ):
            effective_date = DateTime()

        def editContent(obj, effective, expiry):
            kwargs = {}
            # may contain the year
            if effective and (isinstance(effective, DateTime) or len(effective) > 5):
                kwargs["effective_date"] = effective
            # may contain the year
            if expiry and (isinstance(expiry, DateTime) or len(expiry) > 5):
                kwargs["expiration_date"] = expiry
            new_context.plone_utils.contentEdit(obj, **kwargs)

        # You can transition content but not have the permission to ModifyPortalContent
        try:
            editContent(new_context, effective_date, expiration_date)
            contentEditSuccess = 1
        except Unauthorized:
            pass

        wfcontext = context

        # Create the note while we still have access to wfcontext
        note = "Changed status of %s at %s" % (
            wfcontext.title_or_id(),
            wfcontext.absolute_url(),
        )

        if workflow_action in transition_ids:
            wfcontext = new_context.portal_workflow.doActionFor(
                context, workflow_action, comment=comment
            )

        if not wfcontext:
            wfcontext = new_context

        # The object post-transition could now have ModifyPortalContent permission.
        if not contentEditSuccess:
            try:
                editContent(wfcontext, effective_date, expiration_date)
            except Unauthorized:
                pass

        transaction_note(note)

        # If this item is the default page in its parent, attempt to publish that
        # too. It may not be possible, of course
        if plone_utils.isDefaultPage(new_context):
            parent = new_context.aq_inner.aq_parent
            try:
                parent.content_status_modify(
                    workflow_action,
                    comment,
                    effective_date=effective_date,
                    expiration_date=expiration_date,
                )
            except ConflictError:
                raise
            except Exception:
                pass

        context.plone_utils.addPortalMessage(_(u"Item state changed."))
        # TODO: handle state
        return state.set(context=wfcontext)

    def validate(self, workflow_action=""):
        """Validates content publishing.

        Former Validator Python Script validate_content_status_modify.vpy.
        """
        context = self.context
        # TODO: handle state
        if not workflow_action:
            state.setError(
                "workflow_action",
                _(u"This field is required, please provide some " u"information."),
                "workflow_missing",
            )

        if state.getErrors():
            context.plone_utils.addPortalMessage(
                _(u"Please correct the indicated " u"errors."), "error"
            )
            return state.set(status="failure")
        else:
            return state
