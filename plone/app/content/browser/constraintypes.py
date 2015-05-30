# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as PC_
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.autoform.form import AutoExtensibleForm
from z3c.form import button
from z3c.form import form
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import invariant
from zope.interface.exceptions import Invalid
from zope.schema import Choice
from zope.schema import List
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

# XXX
# acquire locallyAllowedTypes from parent (default)
ACQUIRE = -1

# use default behavior of PortalFolder which uses the FTI information
DISABLED = 0

# allow types from locallyAllowedTypes only
ENABLED = 1


ST = lambda key, txt, default: SimpleTerm(value=key,
                                          title=PC_(txt, default=default))

possible_constrain_types = SimpleVocabulary([
    ST(ACQUIRE,
       u'constraintypes_mode_acquire',
       u'Use parent folder settings'),
    ST(DISABLED,
       'label_constraintypes_allow_standard',
       u'Use portal default'),
    ST(ENABLED,
       u'label_constraintypes_specify_manually',
       u'Select manually')
])


@implementer(IVocabularyFactory)
class ValidTypes(object):

    def __call__(self, context):
        constrain_aspect = context.context
        items = []
        for type_ in constrain_aspect.getDefaultAddableTypes():
            items.append(SimpleTerm(value=type_.getId(), title=type_.Title()))
        return SimpleVocabulary(items)

ValidTypesFactory = ValidTypes()


class IConstrainForm(Interface):

    constrain_types_mode = Choice(
        title=PC_("label_type_restrictions", default="Type restrictions"),
        description=PC_("help_add_restriction_mode",
                        default="Select the restriction policy "
                        "in this location"),
        vocabulary=possible_constrain_types,
        required=False,
    )

    allowed_types = List(
        title=PC_("label_immediately_addable_types", default="Allowed types"),
        description=PC_("help_immediately_addable_types",
                        default="Controls what types are addable "
                        "in this location"),
        value_type=Choice(
            source="plone.app.content.ValidAddableTypes"),
        required=False,
    )

    secondary_types = List(
        title=PC_("label_locally_allowed_types", default="Secondary types"),
        description=PC_("help_locally_allowed_types", default=""
                        "Select which types should be available in the "
                        "'More&hellip;' submenu <em>instead</em> of in the "
                        "main pulldown. "
                        "This is useful to indicate that these are not the "
                        "preferred types "
                        "in this location, but are allowed if you really "
                        "need them."
                        ),
        value_type=Choice(
            source="plone.app.content.ValidAddableTypes"),
        required=False,
    )

    @invariant
    def legal_not_immediately_addable(data):
        missing = []
        for one_allowed in data.secondary_types:
            if one_allowed not in data.allowed_types:
                missing.append(one_allowed)
        if missing:
            raise Invalid(
                PC_("You cannot have a type as a secondary type without "
                    "having it allowed. You have selected ${types}s.",
                    mapping=dict(types=", ".join(missing))))
        return True


@implementer(IConstrainForm)
class FormContentAdapter(object):

    def __init__(self, context):
        self.context = ISelectableConstrainTypes(context)

    @property
    def constrain_types_mode(self):
        return self.context.getConstrainTypesMode()

    @property
    def allowed_types(self):
        return self.context.getLocallyAllowedTypes()

    @property
    def secondary_types(self):
        immediately_addable = self.context.getImmediatelyAddableTypes()
        return [t for t in self.context.getLocallyAllowedTypes()
                if t not in immediately_addable]


class ConstrainsFormView(AutoExtensibleForm, form.EditForm):

    schema = IConstrainForm
    label = PC_("heading_set_content_type_restrictions",
                default="Restrict what types of content can be added")
    template = ViewPageTemplateFile("constraintypes.pt")

    def getContent(self):
        return FormContentAdapter(self.context)

    def updateFields(self):
        super(ConstrainsFormView, self).updateFields()
        self.fields['allowed_types'].widgetFactory = CheckBoxFieldWidget
        self.fields['secondary_types'].widgetFactory = CheckBoxFieldWidget

    def updateWidgets(self):
        super(ConstrainsFormView, self).updateWidgets()
        self.widgets['allowed_types'].addClass('current_prefer_form')
        self.widgets['secondary_types'].addClass('current_allow_form')
        self.widgets['constrain_types_mode'].addClass(
            'constrain_types_mode_form')

    @button.buttonAndHandler(u'Save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        allowed_types = data['allowed_types']
        immediately_addable = [
            t for t in allowed_types
            if t not in data['secondary_types']]

        aspect = ISelectableConstrainTypes(self.context)
        aspect.setConstrainTypesMode(data['constrain_types_mode'])
        aspect.setLocallyAllowedTypes(allowed_types)
        aspect.setImmediatelyAddableTypes(immediately_addable)
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
