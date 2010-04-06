import re
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

def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
                optionflags=optionflags,
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
