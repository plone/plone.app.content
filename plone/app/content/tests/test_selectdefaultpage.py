# -*- coding: utf-8 -*-
from plone.app.content.testing import HAS_AT
from plone.app.content.testing import PLONE_APP_CONTENT_DX_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
import transaction
import unittest

if HAS_AT:
    from plone.app.content.testing import PLONE_APP_CONTENT_AT_FUNCTIONAL_TESTING

FOLDER = {'id': 'testfolder',
          'title': 'Test Folder',
          'description': 'Test Folder Description'}

DOCUMENT = {'id': 'testdoc',
            'title': 'Test Document',
            'description': 'Test Document Description'}


class SelectDefaultPageDXTestCase(unittest.TestCase):

    layer = PLONE_APP_CONTENT_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.acl_users.userFolderAddUser(
            'editor', 'secret', ['Editor'], [])

        self._create_structure()
        transaction.commit()

        self.browser = Browser(self.layer['app'])
        self.browser.addHeader('Authorization',
                               'Basic %s:%s' % ('editor', 'secret'))

    def tearDown(self):
        self.portal.manage_delObjects(ids=FOLDER['id'])
        transaction.commit()

    def _createFolder(self):
        self.portal.invokeFactory(id=FOLDER['id'], type_name='Folder')
        folder = getattr(self.portal, FOLDER['id'])
        folder.setTitle(FOLDER['title'])
        folder.setDescription(FOLDER['description'])
        folder.reindexObject()
        # we don't want it in the navigation
        # folder.setExcludeFromNav(True)
        return folder

    def _createDocument(self, context):
        context.invokeFactory(id=DOCUMENT['id'], type_name='Document')
        doc = getattr(context, DOCUMENT['id'])
        doc.setTitle(DOCUMENT['title'])
        doc.setDescription(DOCUMENT['description'])
        doc.reindexObject()
        # we don't want it in the navigation
        # doc.setExcludeFromNav(True)
        return doc

    def _create_structure(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        folder = self._createFolder()
        self._createDocument(folder)
        return folder

    def test_select_default_page_view(self):
        """Check that the form can be rendered."""
        folder = self.portal.testfolder

        self.browser.open('%s/@@select_default_page' % folder.absolute_url())

        self.assertTrue('Select default page' in self.browser.contents)
        self.assertTrue('id="testdoc"' in self.browser.contents)

    def test_select_default_page_view_with_folderish_type(self):
        """Check if folderish types are available."""
        folder = self.portal.testfolder
        folder.invokeFactory(id=FOLDER['id'], type_name='Folder')
        folder2 = getattr(folder, FOLDER['id'])
        folder.setTitle(FOLDER['title'])
        folder2.reindexObject()
        folder_fti = self.portal.portal_types['Folder']
        folder_fti.manage_changeProperties(
            filter_content_types=True, allowed_content_types=[])
        view = folder.restrictedTraverse('@@select_default_page')()

        self.assertTrue('id="testdoc"' in view)
        self.assertTrue('id="testfolder"' in view)

    def test_default_page_action_cancel(self):
        """Check the Cancel action."""
        folder = self.portal.testfolder

        self.browser.open('%s/@@select_default_page' % folder.absolute_url())
        cancel_button = self.browser.getControl(name='form.buttons.Cancel')
        cancel_button.click()

        self.assertEqual(self.browser.url, folder.absolute_url())
        self.assertIs(folder.getDefaultPage(), None)

    def test_default_page_action_save(self):
        """Check the Save action."""
        folder = self.portal.testfolder
        self.browser.open('%s/@@select_default_page' % folder.absolute_url())

        submit_button = self.browser.getControl(name='form.buttons.Save')
        submit_button.click()

        self.assertEqual(self.browser.url, folder.absolute_url())
        self.assertEqual(folder.getDefaultPage(), 'testdoc')


if HAS_AT:
    class SelectDefaultPageATTestCase(SelectDefaultPageDXTestCase):

        layer = PLONE_APP_CONTENT_AT_FUNCTIONAL_TESTING
