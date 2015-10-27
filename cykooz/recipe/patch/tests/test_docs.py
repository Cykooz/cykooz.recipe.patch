# -*- coding: utf-8 -*-
"""
Doctest runner for 'emencia.recipe.patch'.
"""
import doctest
import unittest
import zc.buildout.tests
import zc.buildout.testing

from zope.testing import renormalizing


__docformat__ = 'restructuredtext'


def setUp(test):
    zc.buildout.tests.easy_install_SetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('cykooz.recipe.patch', test)


optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            '../../../../README.rst',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=optionflags,
            checker=renormalizing.RENormalizing([
                # If want to clean up the doctest output you
                # can register additional regexp normalizers
                # here. The format is a two-tuple with the RE
                # as the first item and the replacement as the
                # second item, e.g.
                # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
               zc.buildout.testing.normalize_path
            ]),
        ),
    ))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
