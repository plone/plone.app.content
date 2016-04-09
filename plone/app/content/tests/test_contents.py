# -*- coding: utf-8 -*-
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
