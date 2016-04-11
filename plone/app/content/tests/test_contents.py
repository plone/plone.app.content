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


class ContentsUnitTests(unittest.TestCase):

    def test_get_top_site_from_url(self):
        """Unit test for ``get_top_site_from_url`` with context and request
        mocks.

        Test content structure:
        /approot/PloneSite/folder/SubSite/folder
        PloneSite and SubSite implement ISite
        """
        from plone.app.content.browser.contents import get_top_site_from_url
        from zope.component.interfaces import ISite
        from zope.interface import alsoProvides
        from urlparse import urlparse

        class MockContext(object):
            vh_url = 'http://nohost'
            vh_root = ''

            def __init__(self, physical_path):
                self.physical_path = physical_path
                if self.physical_path.split('/')[-1] in ('PloneSite', 'SubSite'):  # noqa
                    alsoProvides(self, ISite)

            @property
            def id(self):
                return self.physical_path.split('/')[-1]

            def absolute_url(self):
                return self.vh_url + self.physical_path[len(self.vh_root):] or '/'  # noqa

            def restrictedTraverse(self, path):
                return MockContext(self.vh_root + path)

        class MockRequest(object):
            vh_url = 'http://nohost'
            vh_root = ''

            def physicalPathFromURL(self, url):
                # Return the physical path from a URL.
                # The outer right '/' is not part of the path.
                path = self.vh_root + urlparse(url).path.rstrip('/')
                return path.split('/')

        # NO VIRTUAL HOSTING

        req = MockRequest()

        # Case 1:
        ctx = MockContext('/approot/PloneSite')
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'PloneSite')

        # Case 2
        ctx = MockContext('/approot/PloneSite/folder')
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'PloneSite')

        # Case 3:
        ctx = MockContext('/approot/PloneSite/folder/SubSite/folder')
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'PloneSite')

        # VIRTUAL HOSTING ON SUBSITE

        req = MockRequest()
        req.vh_root = '/approot/PloneSite/folder/SubSite'

        # Case 4:
        ctx = MockContext('/approot/PloneSite/folder/SubSite')
        ctx.vh_root = '/approot/PloneSite/folder/SubSite'
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'SubSite')

        # Case 5:
        ctx = MockContext('/approot/PloneSite/folder/SubSite/folder')
        ctx.vh_root = '/approot/PloneSite/folder/SubSite'
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'SubSite')


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
