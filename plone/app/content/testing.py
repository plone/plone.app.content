from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from Products.CMFCore.utils import getToolByName
from zope.configuration import xmlconfig
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import doctest


@implementer(IVocabularyFactory)
class ExampleVocabulary:
    def __call__(self, context, query=None):
        items = ["One", "Two", "Three"]
        tmp = SimpleVocabulary(
            [
                SimpleTerm(it.lower(), it.lower(), it)
                for it in items
                if query is None or query.lower() in it.lower()
            ]
        )
        tmp.test = 1
        return tmp


@provider(IVocabularyFactory)
def ExampleFunctionVocabulary(context, query=None):
    items = ["First", "Second", "Third"]
    tmp = SimpleVocabulary(
        [
            SimpleTerm(it.lower(), it.lower(), it)
            for it in items
            if query is None or query.lower() in it.lower()
        ]
    )
    return tmp


class PloneAppContent(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    USER_NAME = "johndoe"
    USER_PASSWORD = "secret"
    MEMBER_NAME = "janedoe"
    MEMBER_PASSWORD = "secret"
    USER_WITH_FULLNAME_NAME = "jim"
    USER_WITH_FULLNAME_FULLNAME = "Jim Fulton"
    USER_WITH_FULLNAME_PASSWORD = "secret"
    MANAGER_USER_NAME = "manager"
    MANAGER_USER_PASSWORD = "secret"

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.content

        xmlconfig.file(
            "configure.zcml", plone.app.content, context=configurationContext
        )

    def setUpPloneSite(self, portal):
        # Creates some users
        acl_users = getToolByName(portal, "acl_users")
        acl_users.userFolderAddUser(
            self.USER_NAME,
            self.USER_PASSWORD,
            [],
            [],
        )
        acl_users.userFolderAddUser(
            self.MEMBER_NAME,
            self.MEMBER_PASSWORD,
            ["Member"],
            [],
        )
        acl_users.userFolderAddUser(
            self.USER_WITH_FULLNAME_NAME,
            self.USER_WITH_FULLNAME_PASSWORD,
            ["Member"],
            [],
        )
        mtool = getToolByName(portal, "portal_membership", None)
        mtool.addMember("jim", "Jim", ["Member"], [])
        mtool.getMemberById("jim").setMemberProperties(
            {"fullname": "Jim Fult\xc3\xb8rn"}
        )

        acl_users.userFolderAddUser(
            self.MANAGER_USER_NAME,
            self.MANAGER_USER_PASSWORD,
            ["Manager"],
            [],
        )
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")


class NonAsciiLayer(PloneSandboxLayer):
    def setUpZope(self, app, configurationContext):
        import plone.app.content.tests

        xmlconfig.file(
            "profiles/non-ascii-workflow.zcml",
            plone.app.content.tests,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        # applyProfile which has non-ascii characters in state titles
        applyProfile(portal, "plone.app.content.tests:non-ascii-workflow")


PLONE_APP_CONTENT_FIXTURE = PloneAppContent()
PLONE_APP_CONTENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENT_FIXTURE,), name="PloneAppContent:Integration"
)
PLONE_APP_CONTENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENT_FIXTURE,), name="PloneAppContent:Functional"
)


# Dexterity test layers
PLONE_APP_CONTENT_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,), name="PloneAppContentDX:Integration"
)
PLONE_APP_CONTENT_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,), name="PloneAppContentDX:Functional"
)


# Test layer with a workflow containing non-ascii characters in state titles.
PLONE_APP_CONTENT_NON_ASCII_LAYER = NonAsciiLayer()
PLONE_APP_CONTENT_NON_ASCII_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENT_NON_ASCII_LAYER,),
    name="PloneAppContentNonAscii:Integration",
)


optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
)
