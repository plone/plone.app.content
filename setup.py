from setuptools import setup

version = "5.0.1.dev0"

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
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    keywords="plone content views viewlet",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.content",
    license="GPL version 2",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    extras_require=dict(
        test=[
            "plone.app.contenttypes[test]",
            "plone.app.testing",
            "plone.dexterity",
            "plone.testing",
            "Products.GenericSetup",
        ]
    ),
    install_requires=[
        "plone.app.vocabularies>4.1.2",
        "plone.base",
        "plone.i18n",
        "Missing",
        "simplejson",
        "z3c.relationfield",
        "zope.deferredimport",
        "Zope",
    ],
)
