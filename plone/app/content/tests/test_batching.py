from zope.component.testing import setUp, tearDown
import unittest, doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('batching.txt',
                             package='plone.app.content',
                             optionflags=doctest.ELLIPSIS,
                             setUp=setUp, tearDown=tearDown)))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
