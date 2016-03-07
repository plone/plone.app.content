# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.content.namechooser import ATTEMPTS
from plone.app.content.testing import PLONE_APP_CONTENT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.dexterity.fti import DexterityFTI
from zope.container.interfaces import INameChooser
import transaction
import unittest2 as unittest


class NameChooserTest(unittest.TestCase):

    layer = PLONE_APP_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        portal_types = getToolByName(self.portal, "portal_types")
        if 'Document' not in portal_types.objectIds():
            fti = DexterityFTI('Document')
            portal_types._setObject('Document', fti)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_100_or_more_unique_ids(self):
        # add the same item 110 times. the first 100 items should be numbered.
        # after that it should use datetime to generate the id

        holder = self.portal
        title = "A Small Document"
        # create the first object, which will have no suffix
        holder.invokeFactory("Document", id='a-small-document')

        chooser = INameChooser(holder)

        for i in range(1, ATTEMPTS + 1):
            id = chooser.chooseName(title, holder)
            if i <= ATTEMPTS:  # first addition has no suffix
                self.assertEqual("a-small-document-%s" % i, id)
            else:
                self.assertNotEqual("a-small-document-%s" % i, id)

            holder.invokeFactory("Document", id)
            transaction.savepoint(optimistic=True)
            holder.get(id)

    def test_name_starting_with_underscore(self):
        """Regression test

        This test tests for this failure:
        https://github.com/plone/plone.app.content/issues/74
        """
        chooser = INameChooser(self.portal)

        self.assertEqual('cool_image',
                         chooser.chooseName('_cool_image', self.portal))
