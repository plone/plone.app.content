import unittest2 as unittest
from plone.app.content.testing import PLONE_APP_CONTENT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import setRoles, login
import transaction
from plone.app.content.namechooser import ATTEMPTS
from zope.container.interfaces import INameChooser
from Products.CMFPlone.utils import _createObjectByType


class NameChooserTest(unittest.TestCase):
    layer = PLONE_APP_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_100_or_more_unique_ids(self):
        # add the same item 110 times. the first 100 items should be numbered.
        # after that it should use datetime to generate the id
        self.portal.invokeFactory("Folder", 'holder')
        transaction.commit()
        holder = self.portal.get('holder')
        
        title="A Small Document"
        # create the first object, which will have no suffix
        holder.invokeFactory("Document", id='a-small-document')
        transaction.commit()

        chooser = INameChooser(holder)
         
        for i in range(1, ATTEMPTS + 1):
            id = chooser.chooseName(title, holder)
            if i <= ATTEMPTS: # first addition has no suffix
                self.assertEqual("a-small-document-%s"%i, id)
            else:
                self.assertNotEqual("a-small-document-%s"%i, id)

            holder.invokeFactory("Document", id)
            transaction.savepoint(optimistic=True)
            item = holder.get(id)
