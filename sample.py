import sys
from functools import wraps
import inspect

def positional_error(positional, args):
  delt = len(positional) - len(args)
  for arg in positional[-delt:]:
    print 'positioal argument %r not specified' %arg


  print sys.exit(1) # XXX: raise validation error


def build_aliases(defaults):
  aliases = {}
  for key in defaults:
    print 'find alis for %r' % key

    alias = key[0].lower()
    if alias in aliases:
      alias = alias.upper()

      if alias in aliases:
        continue

    aliases[alias] = key


  return aliases

def parse_args(f, *args):
  spec = inspect.getargspec(f)
  positional, defaults, _defaults = list(spec.args), {}, list(spec.defaults)

  while _defaults:
    v = _defaults.pop()
    k = positional.pop()

    defaults[k] = v

  if positional:
    if len(positional) > len(args):
      positional_error(positional, args)

  aliases = build_aliases(defaults)

  kwargs = defaults.copy()
  args, params = args[:len(positional)], list(args[len(positional):])

  while params:
    param = params.pop(0)
    print 'param', param 

    if param.startswith('--'):
      keys = [param[2:]]
    elif param.startswith('-'):
      keys = list(param[1:])
    else:
      print 'ivalid param', param
      sys.exit(1)

    print keys
    while keys:
      key = keys.pop(0)
      print 'key', key

      var = aliases.get(key, key)
      if var not in defaults:
        print 'oops what is %r ?' % var
        sys.exit(1)


      dval = defaults[var]
      print 'default value for %r is %r' % (var, dval)
      if isinstance(dval, bool):
        kwargs[var] = True
        continue

      if keys or not params and dval is None:
        print 'argument %r (%r) requires value' % (key, dval)
        sys.exit(1)

      val = params.pop(0) if params else dval

      kwargs[var] = val


  return args, kwargs

def command(f):
  @wraps(f)
  def command(*args):

    parsed, parsed_kwargs = parse_args(f, *args)

    return f(*parsed, **parsed_kwargs)

  return command

@command
def main(url, dest, verbose=False, secret=None, insecure=False, source_name='default', project=[]):
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
