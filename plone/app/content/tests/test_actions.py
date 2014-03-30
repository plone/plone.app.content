# -*- coding: utf-8 -*-
from plone.app.content.testing import PLONE_APP_CONTENT_AT_INTEGRATION_TESTING
from plone.app.content.testing import PLONE_APP_CONTENT_DX_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from plone.locking.interfaces import ILockable
from z3c.form.interfaces import IFormLayer
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import transaction
import unittest


class ActionsDXTestCase(unittest.TestCase):

    layer = PLONE_APP_CONTENT_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.portal.acl_users.userFolderAddUser(
            'editor', 'secret', ['Editor'], [])

        # For z3c.forms request must provide IFormLayer
        alsoProvides(self.request, IFormLayer)

        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        self.portal.invokeFactory(
            type_name='Folder', id='f1', title='A Test Folder')

        transaction.commit()
        self.browser = Browser(self.layer['app'])
        self.browser.addHeader(
            'Authorization', 'Basic {0}:{1}'.format('editor', 'secret'))

    def tearDown(self):
        self.portal.manage_delObjects(ids='f1')
        transaction.commit()

    def test_delete_confirmation(self):
        folder = self.portal['f1']

        form = folder.restrictedTraverse('delete_confirmation')
        form.update()

        self.assertFalse(form.is_locked)

    def test_delete_confirmation_if_locked(self):
        folder = self.portal['f1']
        lockable = ILockable.providedBy(folder)

        form = getMultiAdapter(
            (folder, self.request), name='delete_confirmation')

        self.assertFalse(form.is_locked)

        if lockable:
            lockable.lock()

        form = getMultiAdapter(
            (folder, self.request), name='delete_confirmation')
        self.assertFalse(form.is_locked)

        # After switching the user it should not be possible to delete the
        # object. Of course this is only possible if our context provides
        # ILockable interface.
        if lockable:
            logout()
            login(self.portal, 'editor')

            form = getMultiAdapter(
                (folder, self.request), name='delete_confirmation')
            self.assertTrue(form.is_locked)

            logout()
            login(self.portal, TEST_USER_NAME)

            ILockable(folder).unlock()

    def test_delete_confirmation_cancel(self):
        folder = self.portal['f1']

        self.browser.open(folder.absolute_url() + '/delete_confirmation')
        self.browser.getControl(name='form.buttons.cancel').click()
        self.assertEqual(self.browser.url, folder.absolute_url())


class ActionsATTestCase(ActionsDXTestCase):

    layer = PLONE_APP_CONTENT_AT_INTEGRATION_TESTING
