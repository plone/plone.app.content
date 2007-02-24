from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='plone.app.content',
      version=version,
      description="Content Views for Plone",
      long_description="""\
plone.app.content contains various views for Plone, such as 
folder_contents, as well as general content infrastructure, such as
base classes and name choosers.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='plone content views viewlet',
      author='Jeroen Vloothuis, Kai Diefenbach',
      author_email='kai.diefenbach@iqpp.de',
      url='http://svn.plone.org/svn/plone/plone.app.content',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.i18n',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
