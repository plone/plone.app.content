# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone.app.content.testing import PLONE_APP_CONTENT_DX_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.fti import DexterityFTI
from plone.protect.authenticator import createToken
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.component import getUtility

import json
import mock
import unittest


class ContentsCopyTests(unittest.TestCase):
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

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_keep_selection_order(self):
        """Keep the order of items the same as they were selected.
        """
        self.portal.invokeFactory('type1', id='f1', title='Folder 1')
        f1 = self.portal.f1
        f1.invokeFactory('type1', id='it1', title='Item 1')
        f1.invokeFactory('type1', id='it2', title='Item 2')
        f1.invokeFactory('type1', id='it3', title='Item 3')

        def _test_order(sel):
            self.request.form['selection'] = json.dumps([
                IUUID(f1[id_])
                for id_
                in sel
            ])
            view = f1.restrictedTraverse('@@fc-copy')
            view()
            self.assertEqual(
                [ob.id for ob in view.oblist],
                sel
            )

        _test_order(['it1', 'it2', 'it3'])
        _test_order(['it3', 'it1', 'it2'])


class ContentsDeleteTests(unittest.TestCase):
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

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_delete_success_with_private_anchestor(self):
        """Delete content item from a folder with private anchestor
        """
        # Create test content /it1/it2/it3
        self.portal.invokeFactory('type1', id='it1', title='Item 1')
        self.portal.it1.invokeFactory('type1', id='it2', title='Item 2')
        self.portal.it1.it2.invokeFactory('type1', id='it3', title='Item 3')
        self.assertEqual(len(self.portal.it1.it2.contentIds()), 1)

        # Block user access to it1m but leave access to its children
        self.portal.it1.__ac_local_roles_block__ = True
        del self.portal.it1.__ac_local_roles__[TEST_USER_ID]
        self.portal.it1.reindexObjectSecurity()
        self.portal.it1.it2.reindexObjectSecurity()

        # Remove test user global roles (leaving only local owner roles on it2)
        setRoles(self.portal, TEST_USER_ID, [])

        # Execute delete request
        selection = [self.portal.it1.it2.it3.UID()]
        self.request.form['folder'] = '/it1/it2'
        self.request.form['selection'] = json.dumps(selection)
        res = self.portal.it1.it2.restrictedTraverse('@@fc-delete')()

        # Check for successful deletion
        res = json.loads(res)
        self.assertEqual(res['status'], 'success')
        self.assertEqual(len(self.portal.it1.it2.contentIds()), 0)

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_delete_success_on_inactive_content(self):
        """Delete an expired content item from a folder.
        """
        # Create content
        self.portal.invokeFactory('type1', id='it1', title='Item 1')
        self.portal.it1.invokeFactory('type1', id='it2', title='Item 2')

        # Expire it2
        exp = datetime.now() - timedelta(days=10)
        self.portal.it1.it2.expiration_date = exp
        self.portal.it1.it2.reindexObject()

        # Remove test user global roles (leaving only local owner roles on it1
        # and below)
        setRoles(self.portal, TEST_USER_ID, [])

        # Execute delete request
        selection = [self.portal.it1.it2.UID()]
        self.request.form['folder'] = '/it1'
        self.request.form['selection'] = json.dumps(selection)
        res = self.portal.it1.restrictedTraverse('@@fc-delete')()

        # Check for successful deletion
        res = json.loads(res)
        self.assertEqual(res['status'], 'success')
        self.assertEqual(len(self.portal.it1.contentIds()), 0)


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

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_paste_success_with_private_anchestor(self):
        """Copy content item and paste into a folder with private anchestor
        """
        # Create test content /it2/it3
        self.portal.invokeFactory('type1', id='it2', title='Item 2')
        self.portal.it2.invokeFactory('type1', id='it3', title='Item 3')
        self.assertEqual(len(self.portal.it2.it3.contentIds()), 0)

        # Block user access to it2, but leave access to its children
        self.portal.it2.__ac_local_roles_block__ = True
        del self.portal.it2.__ac_local_roles__[TEST_USER_ID]
        self.portal.it2.reindexObjectSecurity()
        self.portal.it2.it3.reindexObjectSecurity()

        # Remove test user global roles (leaving only local owner roles on it2)
        setRoles(self.portal, TEST_USER_ID, [])

        # Execute paste
        self.request['__cp'] = self.portal.manage_copyObjects(['it1'])
        self.request.form['folder'] = '/it2/it3'
        res = self.portal.it2.it3.restrictedTraverse('@@fc-paste')()

        # Check for successful paste
        res = json.loads(res)
        self.assertEqual(res['status'], 'success')
        self.assertEqual(len(self.portal.it2.it3.contentIds()), 1)


class ContentsRenameTests(unittest.TestCase):
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

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_rename_success_with_private_anchestor(self):
        """Rename content item from a folder with private anchestor
        """
        # Create test content /it1/it2/it3
        self.portal.invokeFactory('type1', id='it1', title='Item 1')
        self.portal.it1.invokeFactory('type1', id='it2', title='Item 2')
        self.portal.it1.it2.invokeFactory('type1', id='it3', title='Item 3')
        self.assertEqual(len(self.portal.it1.it2.contentIds()), 1)

        # Block user access to it1m but leave access to its children
        self.portal.it1.__ac_local_roles_block__ = True
        del self.portal.it1.__ac_local_roles__[TEST_USER_ID]
        self.portal.it1.reindexObjectSecurity()
        self.portal.it1.it2.reindexObjectSecurity()

        # Remove test user global roles (leaving only local owner roles on it2)
        setRoles(self.portal, TEST_USER_ID, [])

        # Execute rename request
        self.request.form['UID_1'] = self.portal.it1.it2.it3.UID()
        self.request.form['newid_1'] = 'it3bak'
        self.request.form['newtitle_1'] = 'Item 3 BAK'
        res = self.portal.it1.it2.restrictedTraverse('@@fc-rename')()

        # Check for successful deletion
        res = json.loads(res)
        self.assertEqual(res['status'], 'success')
        self.assertEqual(self.portal.it1.it2.it3bak.id, 'it3bak')
        self.assertEqual(self.portal.it1.it2.it3bak.title, 'Item 3 BAK')

    @mock.patch('plone.app.content.browser.contents.ContentsBaseAction.protect', lambda x: True)  # noqa
    def test_rename_success_on_inactive_content(self):
        """Rename an expired content item from a folder.
        """
        # Create content
        self.portal.invokeFactory('type1', id='it1', title='Item 1')
        self.portal.it1.invokeFactory('type1', id='it2', title='Item 2')

        # Expire it2
        exp = datetime.now() - timedelta(days=10)
        self.portal.it1.it2.expiration_date = exp
        self.portal.it1.it2.reindexObject()

        # Remove test user global roles (leaving only local owner roles on it1
        # and below)
        setRoles(self.portal, TEST_USER_ID, [])

        # Execute rename request
        self.request.form['UID_1'] = self.portal.it1.it2.UID()
        self.request.form['newid_1'] = 'it2bak'
        self.request.form['newtitle_1'] = 'Item 2 BAK'
        res = self.portal.it1.restrictedTraverse('@@fc-rename')()

        # Check for successful deletion
        res = json.loads(res)
        self.assertEqual(res['status'], 'success')
        self.assertEqual(self.portal.it1.it2bak.id, 'it2bak')
        self.assertEqual(self.portal.it1.it2bak.title, 'Item 2 BAK')


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
            'plone.app.dexterity.behaviors.metadata.IBasic',
        )
        self.portal.portal_types._setObject('type1', type1_fti)
        self.type1_fti = type1_fti

        # TYPE 2
        type2_fti = DexterityFTI('type1')
        type2_fti.klass = 'plone.dexterity.content.Item'
        type2_fti.filter_content_types = True
        type2_fti.allowed_content_types = []
        type2_fti.behaviors = (
            'plone.app.dexterity.behaviors.metadata.IBasic',
        )
        self.portal.portal_types._setObject('type2', type2_fti)
        self.type2_fti = type2_fti

        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory('type1', id='it1', title='Item 1')
        self.portal.invokeFactory('type2', id='it2', title='Item 2')

    def test_allow_upload(self):
        """Test, if file or images are allowed in a container in different FTI
        configurations.
        """

        # Test non-container, none allowed
        allow_upload = self.portal.it2.restrictedTraverse('@@allow_upload')
        allow_upload = json.loads(allow_upload())

        self.assertEqual(allow_upload['allowUpload'], False)
        self.assertEqual(allow_upload['allowImages'], False)
        self.assertEqual(allow_upload['allowFiles'], False)

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


class FCPropertiesTests(unittest.TestCase):
    layer = PLONE_APP_CONTENT_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # Disable plone.protect for these tests
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.form['_authenticator'] = createToken()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # set available languages
        registry = getUtility(IRegistry)
        registry['plone.available_languages'] = ['en', 'de']

        self.portal.invokeFactory('Folder', 'main1')
        self.portal.main1.invokeFactory('Folder', 'sub1')
        self.portal.main1.sub1.invokeFactory('Folder', 'subsub1')
        self.portal.main1.invokeFactory('Document', 'sub2')
        self.portal.invokeFactory('Document', 'main2')

        self.setup_initial()

    def setup_initial(self):
        # Initial Settings
        self.portal.main1.exclude_from_nav = True
        self.portal.main1.sub1.exclude_from_nav = True
        self.portal.main1.sub1.subsub1.exclude_from_nav = True
        self.portal.main1.sub2.exclude_from_nav = True
        self.portal.main2.exclude_from_nav = True

        self.portal.main1.language = 'en'
        self.portal.main1.sub1.language = 'en'
        self.portal.main1.sub1.subsub1.language = 'en'
        self.portal.main1.sub2.language = 'en'
        self.portal.main2.language = 'en'

    def test_fc_properties__changes__no_recurse(self):
        """Test changing properties without recursion.
        """
        req = self.request
        req.form['language'] = 'de'
        req.form['exclude-from-nav'] = 'no'
        req.form['selection'] = '["{0}", "{1}"]'.format(
            IUUID(self.portal.main1),
            IUUID(self.portal.main2)
        )

        view = getMultiAdapter((self.portal, req), name=u'fc-properties')

        # Call the view and execute the actions
        view()

        self.assertEqual(self.portal.main1.language, 'de')
        self.assertEqual(self.portal.main2.language, 'de')
        self.assertEqual(self.portal.main1.sub1.language, 'en')
        self.assertEqual(self.portal.main1.sub1.subsub1.language, 'en')
        self.assertEqual(self.portal.main1.sub2.language, 'en')

        self.assertEqual(self.portal.main1.exclude_from_nav, False)
        self.assertEqual(self.portal.main2.exclude_from_nav, False)
        self.assertEqual(self.portal.main1.sub1.exclude_from_nav, True)
        self.assertEqual(self.portal.main1.sub1.subsub1.exclude_from_nav, True)
        self.assertEqual(self.portal.main1.sub2.exclude_from_nav, True)

    def test_fc_properties__changes__with_recurse(self):
        """Test changing properties without recursion.
        """
        req = self.request
        req.form['language'] = 'de'
        req.form['exclude-from-nav'] = 'no'
        req.form['recurse'] = 'yes'
        req.form['selection'] = '["{0}", "{1}"]'.format(
            IUUID(self.portal.main1),
            IUUID(self.portal.main2)
        )

        view = getMultiAdapter((self.portal, req), name=u'fc-properties')

        # Call the view and execute the actions
        view()

        self.assertEqual(self.portal.main1.language, 'de')
        self.assertEqual(self.portal.main2.language, 'de')
        self.assertEqual(self.portal.main1.sub1.language, 'de')
        self.assertEqual(self.portal.main1.sub1.subsub1.language, 'de')
        self.assertEqual(self.portal.main1.sub2.language, 'de')

        self.assertEqual(self.portal.main1.exclude_from_nav, False)
        self.assertEqual(self.portal.main2.exclude_from_nav, False)
        self.assertEqual(self.portal.main1.sub1.exclude_from_nav, False)
        self.assertEqual(self.portal.main1.sub1.subsub1.exclude_from_nav, False)  # noqa
        self.assertEqual(self.portal.main1.sub2.exclude_from_nav, False)
