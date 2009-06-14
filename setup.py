from setuptools import setup, find_packages
import os

version = '2.0'

setup(name='plone.app.content',
      version=version,
      description="Content Views for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Framework :: Plone",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
      ],
      keywords='plone content views viewlet',
      author='Jeroen Vloothuis',
      author_email='plone-developers@lists.sourceforge.net',
      url='pypi.python.org/pypi/plone.app.content',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=[
            'zope.publisher',
            'zope.testing',
            'Products.PloneTestCase',
          ]
      ),
      install_requires=[
        'setuptools',
        'plone.memoize',
        'plone.navigation',
        'zope.container',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.component',
        'zope.event',
        'zope.lifecycleevent',
        'zope.schema',
        'zope.viewlet',
        'zope.app.pagetemplate',
        'Products.CMFCore',
        'Products.CMFDefault',
        'Acquisition',
        'Zope2',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
