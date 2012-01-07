import sys
from console_args import command

@command(positional=('dest',))
def main(url, dest=None, verbose=0, secret=None, insecure=False, source_name='default', project=[]):
  print """run with args:
    url: %r
    dest: %r
    verbose: %r
    secret: %r
    insecure: %r
    source: %r
    project: %r
  """ % (url, dest, verbose, secret, insecure, source_name, project)


if __name__ == '__main__':
  main(*sys.argv[1:])
