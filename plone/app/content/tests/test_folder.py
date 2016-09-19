# -*- coding: utf-8 -*-
from plone.app.content.testing import PLONE_APP_CONTENT_FUNCTIONAL_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME

import unittest


class FolderFactoriesTest(unittest.TestCase):
    layer = PLONE_APP_CONTENT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_folder_factories_regression(self):
        from plone.app.content.browser.folderfactories import (
            FolderFactoriesView as FFV)
        view = FFV(self.portal, self.request)
        self.request.form.update({
            'form.button.Add': 'yes',
            'url': self.portal.absolute_url()
        })
        view()
        self.assertEqual(self.request.response.headers.get('location'),
                         self.portal.absolute_url())

    def test_folder_factories(self):
        from plone.app.content.browser.folderfactories import (
            FolderFactoriesView as FFV)
        view = FFV(self.portal, self.request)
        self.request.form.update({
            'form.button.Add': 'yes',
            'url': 'http://www.foobar.com'
        })
        view()
        self.assertNotEqual(self.request.response.headers.get('location'),
                            'http://www.foobar.com')
