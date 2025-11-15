"""Placeholder test"""

import unittest


class TestNothing(unittest.TestCase):
    """The placeholder test class"""

    def test_one_plus_one_equals_two(self):
        """A simple test"""
        self.assertEqual(1 + 1, 2)

    def test_raised_exception_is_raised(self):
        """Wow! Even a raise can be tested!"""
        with self.assertRaises(NotImplementedError):
            raise NotImplementedError
