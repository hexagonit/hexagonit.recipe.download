from zope.testing import renormalizing
import doctest
import os
import pkg_resources
import re
import shutil
import unittest
import zc.buildout.testing
import zc.buildout.tests

BUILDOUT_1 = pkg_resources.get_distribution('zc.buildout').version.startswith('1.')

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('hexagonit.recipe.download', test)


def empty_download_cache(path):
    """Helper function to clear the download cache directory."""
    for element in (os.path.join(path, filename) for filename in os.listdir(path)):
        if os.path.isdir(element):
            shutil.rmtree(element)
        else:
            os.unlink(element)


def test_suite():
    normalizers = [
        zc.buildout.testing.normalize_path,
        (re.compile(r'http://localhost:\d+'), 'http://test.server'),
        # Clean up the variable hashed filenames to avoid spurious test failures
        (re.compile(r'[a-f0-9]{32}'), ''),
    ]

    if BUILDOUT_1:
        # Normalize output differences between zc.buildout 1.x and 2.x
        normalizers.append(
            (re.compile(r'd  buildout\n'), ''))

    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=optionflags,
            globs={
                'empty_download_cache': empty_download_cache,
            },
            checker=renormalizing.RENormalizing(normalizers)
            ),
        ))
    return suite
