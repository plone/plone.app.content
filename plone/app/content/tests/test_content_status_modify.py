from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from Products.CMFPlone.utils import isExpired


class TestContentPublishing(PloneTestCase):
    """ The instant publishing drop down UI.

        This testcase was written to prevent collector/2914 regressions

        In addition, some more general tests of content_status_modify
        have been added, since this seems a logical place to keep them.
    """

    def afterSetUp(self):
        self.portal.acl_users._doAddUser("user1", "secret", ["Member"], [])
        self.membership = self.portal.portal_membership
        self.createMemberarea("user1")
        self.workflow = self.portal.portal_workflow
        self.setupAuthenticator()

    # Test the recursive behaviour of content_status_modify:

    def testPublishingNonDefaultPageLeavesFolderAlone(self):
        self.setRoles(["Manager"])  # Make sure we can publish directly
        self.folder.invokeFactory("Document", id="d1", title="Doc 1")
        self.folder.d1.content_status_modify("publish")
        self.assertEqual(
            self.workflow.getInfoFor(self.folder, "review_state"), "visible"
        )
        self.assertEqual(
            self.workflow.getInfoFor(self.folder.d1, "review_state"), "published"
        )

    def testPublishingDefaultPagePublishesFolder(self):
        self.setRoles(["Manager"])  # Make sure we can publish directly
        self.folder.invokeFactory("Document", id="d1", title="Doc 1")
        self.folder.setDefaultPage("d1")
        self.folder.d1.content_status_modify("publish")
        self.assertEqual(
            self.workflow.getInfoFor(self.folder, "review_state"), "published"
        )
        self.assertEqual(
            self.workflow.getInfoFor(self.folder.d1, "review_state"), "published"
        )

    def testPublishingDefaultPageWhenFolderCannotBePublished(self):
        self.setRoles(["Manager"])  # Make sure we can publish directly
        self.folder.invokeFactory("Document", id="d1", title="Doc 1")
        self.folder.setDefaultPage("d1")
        # make parent be published already when publishing its default document
        # results in an attempt to do it again
        self.folder.content_status_modify("publish")
        self.assertEqual(
            self.workflow.getInfoFor(self.folder, "review_state"), "published"
        )
        self.folder.d1.content_status_modify("publish")
        self.assertEqual(
            self.workflow.getInfoFor(self.folder, "review_state"), "published"
        )
        self.assertEqual(
            self.workflow.getInfoFor(self.folder.d1, "review_state"), "published"
        )

    # test setting effective/expiration date and isExpired method

    def testIsExpiredWithExplicitExpiredContent(self):
        self.setRoles(["Manager"])
        self.folder.invokeFactory("Document", id="d1", title="Doc 1")
        self.folder.d1.content_status_modify(
            workflow_action="publish",
            effective_date="1/1/2001",
            expiration_date="1/2/2001",
        )
        self.assertTrue(isExpired(self.folder.d1))

    def testIsExpiredWithExplicitNonExpiredContent(self):
        self.setRoles(["Manager"])
        self.folder.invokeFactory("Document", id="d1", title="Doc 1")
        self.folder.d1.content_status_modify(workflow_action="publish")
        self.assertFalse(isExpired(self.folder.d1))
