import unittest
import doctest

from Testing import ZopeTestCase as ztc

from base import ContentFunctionalTestCase


def test_suite():
    return unittest.TestSuite((

        ztc.ZopeDocFileSuite(
            'basecontent.txt', package='plone.app.content',
            test_class=ContentFunctionalTestCase,
            optionflags=(doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE)),
    ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
