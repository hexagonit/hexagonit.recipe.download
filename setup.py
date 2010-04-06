from setuptools import setup, find_packages
import os

version = '1.4.0'
name = 'hexagonit.recipe.download'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name=name,
      version=version,
      description="zc.buildout recipe for downloading and extracting packages",
      long_description= (
        read('README.rst')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('hexagonit','recipe','download','README.txt')
        + '\n' +
        'Contributors\n' 
        '***********************\n'
        + '\n' +
        read('CONTRIBUTORS.txt')
        + '\n' +
        'Download\n'
        '***********************\n'
        ),
      classifiers=[
       'Framework :: Buildout',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='development buildout recipe',
      author='Kai Lautaportti',
      author_email='kai.lautaportti@hexagonit.fi',
      url='http://github.com/hexagonit/%s' % name,
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['hexagonit', 'hexagonit.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires = [
        'zc.buildout >= 1.4.0',
        'setuptools'],
      tests_require = ['zope.testing'],
      test_suite = '%s.tests.test_suite' % name,
      entry_points = { 'zc.buildout' : ['default = hexagonit.recipe.download:Recipe'] },
      )
