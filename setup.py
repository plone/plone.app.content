from setuptools import setup, find_packages
import sys, os

version = '1.0rc1'

setup(name='plone.app.content',
      version=version,
      description="Content Views for Plone",
      long_description="""\
plone.app.content contains various views for Plone, such as 
folder_contents, as well as general content infrastructure, such as
base classes and name choosers.
""",
      classifiers=[
          "Framework :: Plone",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
      ],
      keywords='plone content views viewlet',
      author='Jeroen Vloothuis',
      author_email='jeroen.vloothuis@xs4all.nl',
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
