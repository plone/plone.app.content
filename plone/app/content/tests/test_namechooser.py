import doctest
import unittest

from zope.component.testing import setUp, tearDown


def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite(
            "namechooser.txt",
            package="plone.app.content",
            optionflags=doctest.ELLIPSIS,
            setUp=setUp,
            tearDown=tearDown,
        )
    )


if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
