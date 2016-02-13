
from setuptools import setup, find_packages
import os

version = '1.7.2.dev0'
name = 'hexagonit.recipe.download'


def read(*rnames):
    path = os.path.join(os.path.dirname(__file__), *rnames)
    return open(path, 'rb').read().decode('utf-8')

setup(
    name=name,
    version=version,
    description="zc.buildout recipe for downloading and extracting packages",
    long_description=(
        read('README.rst')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('hexagonit', 'recipe', 'download', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
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
        'Framework :: Buildout :: Recipe',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
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
    install_requires=[
        'zc.buildout >= 1.4.0',
        'setuptools',
    ],
    extras_require={
        'test': ['zope.testing', 'manuel'],
    },
    tests_require=['zope.testing', 'manuel'],
    test_suite='hexagonit.recipe.download.tests.test_suite',
    entry_points={'zc.buildout': ['default = hexagonit.recipe.download:Recipe']},
)
