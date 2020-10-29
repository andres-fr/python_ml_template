#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Unit testing of the dummypackage.bar_module. Doc:
https://docs.python.org/3/library/unittest.html#assert-methods
"""


from ml_lib.foo_module import Foo
from ml_lib.bar_module import Bar
from .test_foo import TestcaseFooCpu


class BarTestCaseCpu(TestcaseFooCpu):
    """
    Applies all the Foo tests to Bar, plus an extra inheritance
    test.
    """

    CLASS = Bar

    def test_inheritance(self) -> None:
        """
        Dummy check that Bar inherits from Foo
        """
        b = Bar()
        self.assertIsInstance(b, Bar)
        self.assertIsInstance(b, Foo)

    # def test_fail(self) -> None:
    #     """"""
    #     self.assertTrue(False)
