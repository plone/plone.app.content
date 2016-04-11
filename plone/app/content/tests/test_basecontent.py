# -*- coding: utf-8 -*-
from Testing import ZopeTestCase as ztc
from plone.app.content.tests.base import ContentFunctionalTestCase
import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        ztc.ZopeDocFileSuite(
            'basecontent.rst',
            package='plone.app.content',
            test_class=ContentFunctionalTestCase,
            optionflags=(doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)),
    ))
