# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from zope.configuration import xmlconfig
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import doctest

try:
    import Products.Archetypes
    HAS_AT= True
except ImportError:
    HAS_AT = False


@implementer(IVocabularyFactory)
class ExampleVocabulary(object):

    def __call__(self, context, query=None):
        items = [u'One', u'Two', u'Three']
        tmp = SimpleVocabulary([
            SimpleTerm(it.lower(), it.lower(), it)
            for it in items
            if query is None
            or query.lower() in it.lower()
        ])
        tmp.test = 1
        return tmp


@provider(IVocabularyFactory)
def ExampleFunctionVocabulary(context, query=None):
    items = [u'First', u'Second', u'Third']
    tmp = SimpleVocabulary([
        SimpleTerm(it.lower(), it.lower(), it)
        for it in items
        if query is None
        or query.lower() in it.lower()
    ])
    return tmp


class PloneAppContent(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    USER_NAME = 'johndoe'
    USER_PASSWORD = 'secret'
    MEMBER_NAME = 'janedoe'
    MEMBER_PASSWORD = 'secret'
    USER_WITH_FULLNAME_NAME = 'jim'
    USER_WITH_FULLNAME_FULLNAME = 'Jim Fulton'
    USER_WITH_FULLNAME_PASSWORD = 'secret'
    MANAGER_USER_NAME = 'manager'
    MANAGER_USER_PASSWORD = 'secret'

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.content
        xmlconfig.file(
            'configure.zcml',
            plone.app.content,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        # Creates some users
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser(
            self.USER_NAME,
            self.USER_PASSWORD,
            [],
            [],
        )
        acl_users.userFolderAddUser(
            self.MEMBER_NAME,
            self.MEMBER_PASSWORD,
            ['Member'],
            [],
        )
        acl_users.userFolderAddUser(
            self.USER_WITH_FULLNAME_NAME,
            self.USER_WITH_FULLNAME_PASSWORD,
            ['Member'],
            [],
        )
        mtool = getToolByName(portal, 'portal_membership', None)
        mtool.addMember('jim', 'Jim', ['Member'], [])
        mtool.getMemberById('jim').setMemberProperties(
            {"fullname": 'Jim Fult\xc3\xb8rn'})

        acl_users.userFolderAddUser(
            self.MANAGER_USER_NAME,
            self.MANAGER_USER_PASSWORD,
            ['Manager'],
            [],
        )
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")


if HAS_AT:
    class PloneAppContentAT(PloneAppContent):

        def setUpZope(self, app, configurationContext):
            super(PloneAppContentAT, self).setUpZope(app, configurationContext)
            import Products.ATContentTypes
            xmlconfig.file('configure.zcml',
                           Products.ATContentTypes,
                           context=configurationContext)
            z2.installProduct(app, 'Products.ATContentTypes')

        def setUpPloneSite(self, portal):
            super(PloneAppContentAT, self).setUpPloneSite(portal)
            self.applyProfile(portal, 'Products.ATContentTypes:default')


PLONE_APP_CONTENT_FIXTURE = PloneAppContent()
PLONE_APP_CONTENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENT_FIXTURE, ),
    name="PloneAppContent:Integration")
PLONE_APP_CONTENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENT_FIXTURE, ),
    name="PloneAppContent:Functional")


# Dexterity test layers
PLONE_APP_CONTENT_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE, ),
    name="PloneAppContentDX:Integration")
PLONE_APP_CONTENT_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE, ),
    name="PloneAppContentDX:Functional")


if HAS_AT:
    # AT test layers
    PLONE_APP_CONTENT_AT_FIXTURE = PloneAppContentAT()
    PLONE_APP_CONTENT_AT_INTEGRATION_TESTING = IntegrationTesting(
        bases=(PLONE_APP_CONTENT_AT_FIXTURE, ),
        name="PloneAppContentAT:Integration")
    PLONE_APP_CONTENT_AT_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(PLONE_APP_CONTENT_AT_FIXTURE, ),
        name="PloneAppContentAT:Functional")


optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE
    | doctest.ELLIPSIS
    | doctest.NORMALIZE_WHITESPACE
)
