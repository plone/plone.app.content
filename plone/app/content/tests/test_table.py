import doctest
import unittest

from zope.component.testing import setUp, tearDown


def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite(
            "table.txt",
            package="plone.app.content.browser",
            optionflags=doctest.ELLIPSIS,
            setUp=setUp,
            tearDown=tearDown,
        )
    )
