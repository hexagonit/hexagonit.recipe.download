from zope.testing import doctest
from zope.testing import renormalizing

import os
import re
import shutil
import unittest
import zc.buildout.testing
import zc.buildout.tests

optionflags =  (doctest.ELLIPSIS |
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
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
                optionflags=optionflags,
                globs = {
                    'empty_download_cache' : empty_download_cache,
                },
                checker=renormalizing.RENormalizing([
                        zc.buildout.testing.normalize_path,
                        (re.compile(r'http://localhost:\d+'), 'http://test.server'),
                        # Clean up the variable hashed filenames to avoid spurious test failures
                        (re.compile(r'[a-f0-9]{32}'), ''),
                        ]),
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
