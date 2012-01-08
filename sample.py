import sys
from consoleargs import command

@command(positional=('dest',))
def main(url, dest=[], verbose=0, secret=None, insecure=False, source_name='default', project=[]):
  """
  :param url: where to fetch repo
  :param dest: destination directory
  :param verbose: verbose level
  :param secret: api key
  :param project: to fetch (you can pass many)
  :param insecure: ignore SSL errors
  :param source_name: source name in local config
  """
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
  main()
