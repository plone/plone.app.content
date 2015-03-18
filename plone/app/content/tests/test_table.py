from zope.component.testing import setUp, tearDown
import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('table.txt',
                             package='plone.app.content.browser',
                             optionflags=doctest.ELLIPSIS,
                             setUp=setUp, tearDown=tearDown)))
