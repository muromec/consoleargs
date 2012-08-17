#coding: utf-8


import sys
import unittest
from cStringIO import StringIO

from consoleargs import *


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.old_stdout = sys.stdout
        sys.stdout = self.stdout = StringIO()
        self.old_argv = sys.argv
        sys.argv = self.argv = []

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.argv = self.old_argv


class BuildAliasesTest(BaseTest):

    def test_simple_alias(self):
        params = {'verbose': None}
        aliases = build_aliases(params)
        self.assertEqual(aliases, {'v': 'verbose'})

    def test_alias_with_underscore(self):
        params = {'verbose_level': None}
        aliases = build_aliases(params)
        self.assertEqual(aliases, {
            'verbose-level': 'verbose_level',
            'v': 'verbose_level'
        })

    def test_aliases_with_same_first_symbol(self):
        """
        This test shows that it is no support for more than 2 aliases
        """
        params = {'verbose': None, 'verb': None, 'veto': None}
        aliases = build_aliases(params)
        self.assertEqual(aliases, {
            'V': 'verb',
            'v': 'veto'
        })


class PositionalErrorTest(BaseTest):

    def test_simple(self):
        positional = ['in', 'out']
        args = ()
        self.assertRaises(ArgError, positional_error, positional, args)
        expected_out = ''.join('Positional argument %r not specified\n'\
                                % arg for arg in positional)
        self.assertEqual(self.stdout.getvalue(), expected_out)


class CommandDecoratorTest(BaseTest):

    def test_with_no_params(self):
        def foo():
            return 42

        self.assertEqual(command()(foo)(), 42)

    def test_with_first_param_callable(self):
        """
        I don't know why we need this
        """
        def foo():
            return 42

        self.assertEqual(command(foo)(), 42)

    def test_with_function_args(self):
        def foo(verbose=0, color=[]):
            return verbose, color

        sys.argv = ['--verbose', '--color=red']
        wrapped_foo = command()(foo)
        self.assertEqual(wrapped_foo('--verbose', '--color=red'), (1, ['red']))

    def test_with_int_argv_option(self):
        def foo(verbose=0, color=[]):
            return verbose, color

        sys.argv = ['--verbose', '--color=red']
        self.assertEqual(command(argv=1)(foo)(), (0, ['red']))

    def test_with_false_argv_option(self):
        def foo(verbose=0, color=[]):
            return verbose, color

        sys.argv = ['--verbose', '--color=red']
        self.assertEqual(command(argv=False)(foo)(), (0, []))

    def test_with_list_argv_option(self):
        def foo(path='.', verbose=0, color=[]):
            return path, verbose, color

        sys.argv = ['--path=../', '--verbose', '--color=red']
        wrapped_foo = command(argv=(1, 2))(foo)
        self.assertEqual(wrapped_foo(), ('.', 1, []))

    def test_list_argv_option_wrong_length(self):
        def foo(path='.', verbose=0, color=[]):
            return path, verbose, color

        wrapped_foo = command(argv=(1, 2, 3))(foo)
        # error at :240
        # list is tuple and length is not equal 2
        self.assertRaises(TypeError, wrapped_foo)

    def test_list_argv_option_wrong_type(self):
        def foo(path='.', verbose=0, color=[]):
            return path, verbose, color

        wrapped_foo = command(argv=('first', 'last'))(foo)
        self.assertRaises(TypeError, wrapped_foo)

        wrapped_foo = command(argv={'test': 42})(foo)
        self.assertRaises(TypeError, wrapped_foo)

    def test_list_argv_option_with_function_required_params(self):
        def foo(width, height, verbose=0, color=[]):
            return width, height, verbose, color

        sys.argv = ['200', '200', '--verbose', '--color=red']
        wrapped_foo = command(argv=(2, 3))(foo)
        # throws ArgError and returns 1 because of required width and height
        self.assertRaises(SystemExit, wrapped_foo)

        sys.argv = ['400', '400', '200', '200', '--verbose', '--color=red']
        wrapped_foo = command(argv=(2, 5))(foo)
        self.assertEqual(wrapped_foo(), ('200', '200', 1, []))


class ParseArgsTest(BaseTest):
    def test_help_called(self):
        def foo():
            pass
        self.assertRaises(ArgError, parse_args, foo, '-h')
        self.assertRaises(ArgError, parse_args, foo, '--help')


if __name__ == '__main__':
    unittest.main()
