from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='plone.app.views',
      version=version,
      description="Views for Plone",
      long_description="""\
plone.app.views contains various views for Plone, such as 
folder_contents.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='plone views viewlet',
      author='Jeroen Vloothuis, Kai Diefenbach',
      author_email='kai.diefenbach@iqpp.de',
      url='http://svn.plone.org/svn/plone/plone.app.views',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
