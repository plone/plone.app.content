# -*- coding: utf-8 -*-
from plone.app.content.testing import PLONE_APP_CONTENT_DX_FUNCTIONAL_TESTING
from plone.app.content.testing import optionflags
from plone.testing import layered
import doctest
import unittest


doctests = (
    'basecontent.rst',
)


def test_suite():
    suite = unittest.TestSuite()
    tests = [
        layered(
            doctest.DocFileSuite(
                test_file,
                package='plone.app.content',
                optionflags=optionflags,
            ),
            layer=PLONE_APP_CONTENT_DX_FUNCTIONAL_TESTING,
        )
        for test_file in doctests
    ]
    suite.addTests(tests)
    return suite
