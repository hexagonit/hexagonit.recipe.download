import os
import re
import shutil
import unittest
import zc.buildout.testing
import zc.buildout.tests

from zope.testing import doctest, renormalizing

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

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
                        # Use a static MD5 sum for the tests
                        (re.compile(r'[a-f0-9]{32}'), 'dfb1e3136ba092f200be0f9c57cf62ec'),
                        ]),
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
