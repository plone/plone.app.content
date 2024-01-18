from setuptools import find_packages
from setuptools import setup


version = "4.1.1"

setup(
    name="plone.app.content",
    version=version,
    description="Content Views for Plone",
    long_description="\n\n".join(
        [
            open("README.rst").read(),
            open("CHANGES.rst").read(),
        ]
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="plone content views viewlet",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.content",
    license="GPL version 2",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    extras_require=dict(
        test=[
            "plone.app.contenttypes[test]",
            "plone.app.testing",
            "plone.dexterity",
            "plone.namedfile",
            "plone.testing",
            "zope.annotation",
            "Products.GenericSetup",
        ]
    ),
    install_requires=[
        "plone.app.dexterity",
        "plone.app.querystring",
        "plone.app.uuid",
        "plone.app.vocabularies>4.1.2",
        "plone.app.z3cform",
        "plone.autoform",
        "plone.base",
        "plone.i18n",
        "plone.folder",
        "plone.locking",
        "plone.memoize",
        "plone.protect",
        "plone.supermodel",
        "plone.uuid",
        "Missing",
        "Products.MimetypesRegistry",
        "Products.PortalTransforms",
        "Products.statusmessages",
        "simplejson",
        "z3c.relationfield",
        "z3c.form",
        "zope.browsermenu",
    ],
)
