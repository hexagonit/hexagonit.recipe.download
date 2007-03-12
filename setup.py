from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='hexagonit.recipe.download',
      version=version,
      description="zc.buildout download recipe",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Kai Lautaportti',
      author_email='kai.lautaportti@hexagonit.fi',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['hexagonit', 'hexagonit.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires = ['zc.buildout', 'setuptools'],
      dependency_links = ['http://download.zope.org/distribution/'],
      entry_points = { 'zc.buildout' : ['default = hexagonit.recipe.download:Recipe'] },
      )
