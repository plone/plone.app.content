from setuptools import setup, find_packages

version = '2.0.12'

setup(name='plone.app.content',
      version=version,
      description="Content Views for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
          "Framework :: Plone",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
      ],
      keywords='plone content views viewlet',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.content',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=[
            'zope.testing',
            'Products.PloneTestCase',
          ]
      ),
      install_requires=[
        'setuptools',
        'plone.memoize',
        'plone.i18n',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.component',
        'zope.container',
        'zope.event',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        'zope.viewlet',
        'Acquisition',
        'Products.CMFPlone',
        'Products.CMFCore>=2.2.0dev',
        'Products.CMFDefault',
        'Zope2',
      ],
      )
