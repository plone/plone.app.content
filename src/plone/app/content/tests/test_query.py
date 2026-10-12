from plone.app.content.testing import PLONE_APP_CONTENT_DX_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.indexing import processQueue
from Products.CMFCore.utils import getToolByName

import json
import unittest

TAG = "sometag"
MEMBER = "member"


class QueryStringIndexOptionsTests(unittest.TestCase):
    layer = PLONE_APP_CONTENT_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.portal.invokeFactory("Folder", "folder", title="Folder")
        self.folder = self.portal.folder
        self.portal.portal_workflow.doActionFor(self.folder, "publish")
        self.folder.invokeFactory("Document", "document", title="Document")
        self.folder.document.subject = (TAG,)
        self.folder.document.reindexObject(idxs=["Subject"])
        # the keywords vocabulary reads the Subject index directly
        processQueue()

        mtool = getToolByName(self.portal, "portal_membership")
        mtool.addMember(MEMBER, "secret", ["Member"], [])
        mtool.getMemberById(MEMBER).setMemberProperties({"fullname": "Local Editor"})

    def _get_options(self, context):
        return json.loads(context.restrictedTraverse("@@qsOptions")())

    def test_available_on_any_context(self):
        """The view is not restricted to the navigation root."""
        options = self._get_options(self.folder)

        self.assertIn("Subject", options["indexes"])

    def test_vocabulary_values_for_manager(self):
        options = self._get_options(self.portal)

        self.assertIn(TAG, options["indexes"]["Subject"]["values"])

    def test_vocabulary_values_for_local_editor(self):
        """A user who may edit only in this folder gets the tags there."""
        self.folder.manage_setLocalRoles(MEMBER, ["Editor"])
        login(self.portal, MEMBER)

        options = self._get_options(self.folder)

        self.assertIn(TAG, options["indexes"]["Subject"]["values"])

    def test_vocabulary_values_for_local_editor_via_path_parameter(self):
        """folder_contents asks at the navigation root and sends the folder path."""
        self.folder.manage_setLocalRoles(MEMBER, ["Editor"])
        login(self.portal, MEMBER)
        self.request.form["path"] = "/folder"

        options = self._get_options(self.portal)

        self.assertIn(TAG, options["indexes"]["Subject"]["values"])

    def test_no_vocabulary_values_for_unknown_path(self):
        self.folder.manage_setLocalRoles(MEMBER, ["Editor"])
        login(self.portal, MEMBER)
        self.request.form["path"] = "/does-not-exist"

        options = self._get_options(self.portal)

        self.assertEqual(options["indexes"]["Subject"]["values"], {})

    def test_path_parameter_only_accepts_content(self):
        """restrictedTraverse also returns views, tools, attributes and methods."""
        self.folder.manage_setLocalRoles(MEMBER, ["Editor"])
        login(self.portal, MEMBER)
        self.request.form["path"] = "/folder/@@edit"

        options = self._get_options(self.portal)

        self.assertEqual(options["indexes"]["Subject"]["values"], {})

    def test_path_parameter_does_not_bypass_the_permission_check(self):
        self.portal.invokeFactory("Folder", "private", title="Private")
        self.folder.manage_setLocalRoles(MEMBER, ["Editor"])
        login(self.portal, MEMBER)
        self.request.form["path"] = "/private"

        options = self._get_options(self.portal)

        self.assertEqual(options["indexes"]["Subject"]["values"], {})

    def test_no_vocabulary_values_for_local_editor_on_portal_root(self):
        """The permission is still checked, now against the context asked for."""
        self.folder.manage_setLocalRoles(MEMBER, ["Editor"])
        login(self.portal, MEMBER)

        options = self._get_options(self.portal)

        self.assertEqual(options["indexes"]["Subject"]["values"], {})

    def test_no_vocabulary_values_without_edit_permission(self):
        login(self.portal, MEMBER)

        options = self._get_options(self.folder)

        self.assertEqual(options["indexes"]["Subject"]["values"], {})

    def test_user_vocabulary_values_for_manager(self):
        options = self._get_options(self.portal)

        self.assertIn(MEMBER, options["indexes"]["Creator"]["values"])

    def test_no_user_vocabulary_values_without_edit_permission(self):
        """The users vocabulary stays closed, see plone/plone.restapi#1777."""
        login(self.portal, MEMBER)

        options = self._get_options(self.folder)

        self.assertEqual(options["indexes"]["Creator"]["values"], {})
