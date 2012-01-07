
Argument parser for humans
==========================

This library implements simple argument parser,
based on function signature and docstring messages

Usage
=====

Usage example:

    >>> from console_args import command
    >>> @command
    >>> def main(destination, name=None, verbose=0):
    >>>   print destination, name, verbose
