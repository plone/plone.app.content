# -*- coding: utf-8 -*-
from zope.component.testing import setUp
from zope.component.testing import tearDown
import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('namechooser.txt',
                             package='plone.app.content',
                             optionflags=doctest.ELLIPSIS,
                             setUp=setUp, tearDown=tearDown)))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
