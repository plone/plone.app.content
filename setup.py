from setuptools import find_packages, setup

version = "4.0.0a10"

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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
    extras_require=dict(
        test=[
            "plone.app.contenttypes",
            "plone.app.testing",
        ]
    ),
    install_requires=[
        "Acquisition",
        "plone.app.widgets",
        "plone.batching",
        "plone.i18n",
        "plone.memoize",
        "plone.protect",
        "Products.CMFCore>=2.2.0dev",
        "Products.CMFDynamicViewFTI",  # required for cmf.ModifyViewTemplate
        "plone.app.vocabularies>4.1.2",
        "setuptools",
        "simplejson",
        "z3c.form",
        "zope.component",
        "zope.container",
        "zope.event",
        "zope.i18n",
        "zope.i18nmessageid",
        "zope.interface",
        "zope.lifecycleevent",
        "zope.publisher",
        "zope.schema",
        "Zope",
    ],
)
