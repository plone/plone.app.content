from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import form, field, button
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface


_ = MessageFactory('Plone')


class IOwnershipForm(Interface):
    owner = schema.Choice(
        title=_(u"label_new_owner", default=u"New owner"),
        description=_(
            u'help_change_ownership',
            default='Changes the ownership of the current object.'),
        source='plone.app.users.Users',
        required=True,
        )

    subobjects = schema.Bool(
        title=_(u'label_subobjects', default=u'Subobjects'),
        description=_(
            u"help_subobjects",
            default=u'Changes all the contained objects if selected.')
        )


class ChangeOwnershipForm(form.Form):
    fields = field.Fields(IOwnershipForm)
    ignoreContext = True

    @button.buttonAndHandler(_(u'Save'))
    def save(self, event):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        owner = data['owner']

        subobjects = 0
        if data.get('subobjects'):
            subobjects = 1

        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.changeOwnershipOf(
            self.context, owner, recursive=subobjects)

        IStatusMessage(self.request).addStatusMessage(
            _(u"Ownership has been changed."))

        return self.request.response.redirect(self.context.absolute_url())
