
Argument parser for humans
==========================

This library implements simple argument parser,
based on function signature and docstring messages

Usage
=====

Usage example:

    >>> from consoleargs import command
    >>> @command
    >>> def main(destination, name=None, verbose=0):
    >>>   """
    >>>    :param destination: Where to look
    >>>    :param name: Whot to search
    >>>    :param verbose: How much to talk
    >>>   """
    >>>   print destination, name, verbose
