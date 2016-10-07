# -*- coding: utf-8 -*-
from plone.app.content.testing import PLONE_APP_CONTENT_DX_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.fti import DexterityFTI

import json
import mock
import unittest


class ContentsPasteTests(unittest.TestCase):
    layer = PLONE_APP_CONTENT_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # TYPE 1
        type1_fti = DexterityFTI('type1')
        type1_fti.klass = 'plone.dexterity.content.Container'
        type1_fti.filter_content_types = True
        type1_fti.allowed_content_types = ['type1']
        type1_fti.behaviors = (
            'Products.CMFPlone.interfaces.constrains.ISelectableConstrainTypes',  # noqa
            'plone.app.dexterity.behaviors.metadata.IBasic'
        )
        self.portal.portal_types._setObject('type1', type1_fti)
        self.type1_fti = type1_fti

        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory('type1', id='it1', title='Item 1')

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_paste_success(self):
        """Copy content item and paste in portal root.
        """
        # # setup copying via @@fc-copy
        # from plone.uuid.interfaces import IUUID
        # self.request['selection'] = [IUUID(self.portal.it1)]
        # self.portal.restrictedTraverse('@@fc-copy')()

        self.request['__cp'] = self.portal.manage_copyObjects(['it1'])
        self.request.form['folder'] = '/'
        res = self.portal.restrictedTraverse('@@fc-paste')()

        res = json.loads(res)
        self.assertEqual(res['status'], 'success')
        self.assertEqual(len(self.portal.contentIds()), 2)

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_paste_success_paste_in_itself(self):
        """Copy content item and paste in itself. Because we can.
        """
        self.request['__cp'] = self.portal.manage_copyObjects(['it1'])
        self.request.form['folder'] = '/it1'
        res = self.portal.it1.restrictedTraverse('@@fc-paste')()

        res = json.loads(res)
        self.assertEqual(res['status'], 'success')
        self.assertEqual(len(self.portal.it1.contentIds()), 1)

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_paste_fail_constraint(self):
        """Fail pasting content item in itself when folder constraints don't
        allow to.
        """
        self.type1_fti.allowed_content_types = []  # set folder constraints
        self.request['__cp'] = self.portal.manage_copyObjects(['it1'])
        self.request.form['folder'] = '/it1'
        res = self.portal.it1.restrictedTraverse('@@fc-paste')()

        res = json.loads(res)
        self.assertEqual(res['status'], 'warning')
        self.assertEqual(len(self.portal.it1.contentIds()), 0)


class AllowUploadViewTests(unittest.TestCase):
    layer = PLONE_APP_CONTENT_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # TYPE 1
        type1_fti = DexterityFTI('type1')
        type1_fti.klass = 'plone.dexterity.content.Container'
        type1_fti.filter_content_types = True
        type1_fti.allowed_content_types = []
        type1_fti.behaviors = (
            'plone.app.dexterity.behaviors.metadata.IBasic'
        )
        self.portal.portal_types._setObject('type1', type1_fti)
        self.type1_fti = type1_fti

        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory('type1', id='it1', title='Item 1')

    def test_allow_upload(self):
        """Test, if file or images are allowed in a container in different FTI
        configurations.
        """

        # Test none allowed
        self.type1_fti.allowed_content_types = []
        allow_upload = self.portal.it1.restrictedTraverse('@@allow_upload')
        allow_upload = json.loads(allow_upload())

        self.assertEqual(allow_upload['allowUpload'], False)
        self.assertEqual(allow_upload['allowImages'], False)
        self.assertEqual(allow_upload['allowFiles'], False)

        # Test images allowed
        self.type1_fti.allowed_content_types = ['Image']
        allow_upload = self.portal.it1.restrictedTraverse('@@allow_upload')
        allow_upload = json.loads(allow_upload())

        self.assertEqual(allow_upload['allowUpload'], True)
        self.assertEqual(allow_upload['allowImages'], True)
        self.assertEqual(allow_upload['allowFiles'], False)

        # Test files allowed
        self.type1_fti.allowed_content_types = ['File']
        allow_upload = self.portal.it1.restrictedTraverse('@@allow_upload')
        allow_upload = json.loads(allow_upload())

        self.assertEqual(allow_upload['allowUpload'], True)
        self.assertEqual(allow_upload['allowImages'], False)
        self.assertEqual(allow_upload['allowFiles'], True)

        # Test images and files allowed
        self.type1_fti.allowed_content_types = ['Image', 'File']
        allow_upload = self.portal.it1.restrictedTraverse('@@allow_upload')
        allow_upload = json.loads(allow_upload())

        self.assertEqual(allow_upload['allowUpload'], True)
        self.assertEqual(allow_upload['allowImages'], True)
        self.assertEqual(allow_upload['allowFiles'], True)

        # Test files allowed, path via request variable
        self.type1_fti.allowed_content_types = ['File']
        # First, test on Portal root to see the difference
        allow_upload = self.portal.restrictedTraverse('@@allow_upload')
        allow_upload = json.loads(allow_upload())
        self.assertEqual(allow_upload['allowUpload'], True)
        self.assertEqual(allow_upload['allowImages'], True)
        self.assertEqual(allow_upload['allowFiles'], True)
        # Then, with path set to sub item
        allow_upload = self.portal.restrictedTraverse('@@allow_upload')
        allow_upload.request.form['path'] = '/plone/it1'
        allow_upload = json.loads(allow_upload())
        self.assertEqual(allow_upload['allowUpload'], True)
        self.assertEqual(allow_upload['allowImages'], False)
        self.assertEqual(allow_upload['allowFiles'], True)
