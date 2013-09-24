from Products.CMFCore.utils import getToolByName

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from zope.configuration import xmlconfig


class PloneAppContent(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

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
        xmlconfig.file('configure.zcml',
                       plone.app.content,
                       context=configurationContext)

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

PLONE_APP_CONTENT_FIXTURE = PloneAppContent()
PLONE_APP_CONTENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENT_FIXTURE,),
    name="PloneAppContent:Integration")
PLONE_APP_CONTENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENT_FIXTURE,),
    name="PloneAppContent:Functional")
