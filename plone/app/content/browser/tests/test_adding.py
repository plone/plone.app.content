import unittest

from Acquisition import aq_get
from Products.PloneTestCase import PloneTestCase as ptc

ptc.setupPloneSite()


class AddingTests(ptc.PloneTestCase):

    def test_adding_acquisition(self):
        adding = self.portal.unrestrictedTraverse('+')
        # Check explicit Acquisition
        template = aq_get(adding, 'main_template')
        self.assertTrue(template)
        # Check implicit Acquisition, unfortunately the CMF skins machinery
        # depends on this
        template = getattr(adding, 'main_template')
        self.assertTrue(template)
        # Check traversal
        self.assertTrue(self.portal.unrestrictedTraverse('+/main_template'))


def test_suite():
    return unittest.makeSuite(AddingTests)
