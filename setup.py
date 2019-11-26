# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '3.5.7'

setup(
    name='plone.app.content',
    version=version,
    description="Content Views for Plone",
    long_description='\n\n'.join([
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ]),
    classifiers=[
        "Development Status :: 6 - Mature",
        "Framework :: Plone",
        "Framework :: Plone :: 5.1",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='plone content views viewlet',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.org/project/plone.app.content',
    license='GPL version 2',
    packages=find_packages(),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'plone.app.contenttypes',
            'plone.app.testing',
            'mock'
        ]
    ),
    install_requires=[
        'Acquisition',
        'plone.app.widgets',
        'plone.batching',
        'plone.i18n',
        'plone.memoize',
        'plone.protect',
        'Products.CMFCore>=2.2.0dev',
        'Products.CMFDynamicViewFTI',  # required for cmf.ModifyViewTemplate
        'Products.CMFPlone',
        'setuptools',
        'simplejson',
        'six',
        'zope.component',
        'zope.container',
        'zope.deferredimport',
        'zope.event',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        'Zope2',
    ],
)
