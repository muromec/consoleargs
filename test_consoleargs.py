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
        self.assertRaises(ArgError, parse_args, foo, 'test', '42', '-h')
        self.assertRaises(ArgError, parse_args, foo, 'test', '42', '--help')

    def test_simple_args(self):
        def foo(arg1, arg2):
            pass

        error_msg = '''Positional argument '%s' not specified\n'''

        self.assertEqual(parse_args(foo, 'test', '42'), (['test', '42'], {}))

        self.assertRaises(ArgError, parse_args, foo)
        self.assertEqual(self.stdout.getvalue(), error_msg * 2 % ('arg1', 'arg2'))

        self.stdout.truncate(0)

        self.assertRaises(ArgError, parse_args, foo, 'test')
        self.assertEqual(self.stdout.getvalue(), error_msg % 'arg2')

    def test_default_boolean_arg(self):
        def foo(bar=False):
            pass

        self.assertEqual(parse_args(foo), ([], {'bar': False}))
        self.assertEqual(parse_args(foo, '-b'), ([], {'bar': True}))
        self.assertEqual(parse_args(foo, '--bar'), ([], {'bar': True}))

    def test_default_integer_arg(self):
        def foo(bar=0):
            pass

        self.assertEqual(parse_args(foo), ([], {'bar': 0}))
        self.assertEqual(parse_args(foo, '-b'), ([], {'bar': 1}))
        self.assertEqual(parse_args(foo, '--bar'), ([], {'bar': 1}))
        self.assertEqual(parse_args(foo, '-bb'), ([], {'bar': 2}))
        self.assertEqual(parse_args(foo, '-b', '-b'), ([], {'bar': 2}))
        self.assertEqual(parse_args(foo, '--b', '--bar'), ([], {'bar': 2}))
        self.assertEqual(parse_args(foo, '--bar', '--bar'), ([], {'bar': 2}))
        self.assertEqual(parse_args(foo, '--bar', '5'), ([], {'bar':5}))
        self.assertEqual(parse_args(foo, '-b', '9'), ([], {'bar':9}))
        self.assertEqual(parse_args(foo, '-b', '1423'), ([], {'bar':1423}))
        self.assertEqual(parse_args(foo, '-b', '0x11'), ([], {'bar':17}))

    def test_default_list_arg(self):
        def foo(bar=[]):
            pass

        self.assertEqual(parse_args(foo), ([], {'bar': []}))
        self.assertEqual(parse_args(foo, '--b=baz'), ([], {'bar': ['baz']}))
        self.assertEqual(parse_args(foo, '--bar=baz'), ([], {'bar': ['baz']}))
        self.assertEqual(
            parse_args(foo, '--b=bar', '--b=qux'), ([], {'bar': ['bar', 'qux']})
        )
        self.assertEqual(
            parse_args(foo, '--bar=baz', '--bar=qux'),
            ([], {'bar': ['baz', 'qux']})
        )

        self.assertRaises(ArgError, parse_args, foo, '-b=baz')

    def test_default_str_arg(self):
        def foo(bar='baz'):
            pass

        self.assertEqual(parse_args(foo), ([], {'bar': 'baz'}))
        self.assertEqual(parse_args(foo, '--b=qux'), ([], {'bar': 'qux'}))
        self.assertEqual(parse_args(foo, '--bar=qux'), ([], {'bar': 'qux'}))
        self.assertEqual(parse_args(foo, '--bar='), ([], {'bar': ''}))

        self.assertRaises(ArgError, parse_args, foo, '-b=qux')

    def test_unknown_arg(self):
        def foo(bar=None):
            pass

        self.assertRaises(ArgError, parse_args, foo, '--baz')
        self.assertEqual(self.stdout.getvalue(), '''oops what is 'baz' ?\n''')

    def test_wrong_list_arg(self):
        def foo(bar=[]):
            pass

        # this is strange
        self.assertEqual(parse_args(foo, '--bar'), ([], {'bar': [[]]}))

    def test_positional_arg(self):
        def foo(bar, baz=[]):
            pass

        self.assertEqual(
            parse_args(foo, 'val', '42', 'qux', positional='baz'),
            (['val', ['42', 'qux']], {})
        )

    def test_require_value(self):
        def foo(bar=None):
            pass

        self.assertRaises(ArgError, parse_args, foo, '--bar')
        self.assertEqual(self.stdout.getvalue(),
            '''argument 'bar' (None) requires value\n''')

    def test_all_help(self):
        def foo(bar=[]):
            pass

        #Why we need this?
        self.assertRaises(ArgError, parse_args, foo, 'help', all_help=False)
        self.failUnlessRaises(ArgError, parse_args, foo, 'help')


if __name__ == '__main__':
    unittest.main()
