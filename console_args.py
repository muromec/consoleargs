from functools import wraps
import inspect

class ArgError(Exception):
  pass

def positional_error(positional, args):
  delt = len(positional) - len(args)
  for arg in positional[-delt:]:
    print 'positioal argument %r not specified' %arg

  raise ArgError


def build_aliases(defaults):
  aliases = {}
  for key in defaults:

    if '_' in key:
      aliases[key.replace('_', '-')] = key

    alias = key[0].lower()
    if alias in aliases:
      alias = alias.upper()

      if alias in aliases:
        continue

    aliases[alias] = key


  return aliases

def build_help(func, positional, defaults, aliases):
  if callable(func):
    import sys
    mod = sys.modules.get(func.__module__)
    name = mod.__file__
  else:
    name = func

  msg = "Usage %(progname)s " % {"progname": name}
  kwargs = list(defaults.keys())
  for arg in positional:
    if arg in kwargs:
      msg += '[%s] ' % arg.upper()
      kwargs.remove(arg)
    else:
      msg += '%s ' % arg.upper()

  if kwargs:
    msg += '[OPTIONS]'

  msg += '\n\nOptions:\n'

  back_alias = {}
  for alias, arg in aliases.items():
    other = back_alias.get(arg) or []
    other.append(alias)
    back_alias[arg] = other

  for arg in kwargs:
    msg += '\t--%s ' % arg
    for alias in back_alias.get(arg) or []:
      if len(alias):
        msg += '-%s ' % alias
      else:
        msg += '--%s ' % alias

    msg += '\n'

  return msg

def parse_args(f, *args, **opts):
  spec = inspect.getargspec(f)
  positional, defaults, _defaults = list(spec.args), {}, list(spec.defaults)
  _positional = opts.get('positional') or []
  required = positional[:]

  while _defaults:
    v = _defaults.pop()
    k = positional[-1]

    if k not in _positional:
      positional.pop()

    required.pop()

    defaults[k] = v

  aliases = build_aliases(defaults)
  help_msg = build_help(f, positional, defaults, aliases)

  if args and args[0] in ['--help', '-h']:
    print help_msg
    raise ArgError

  if positional:
    if len(required) > len(args):
      positional_error(positional, args)

  kwargs = defaults.copy()

  params, args = list(args), []
  while params:
    param = params.pop(0)

    if param.startswith('--'):
      keys = [param[2:]]
    elif param.startswith('-'):
      keys = list(param[1:])
    elif param == 'help':
      print help_msg
      raise ArgError

    elif len(args) < len(positional):
      args.append(param)
      continue
    else:
      print 'ivalid param', param
      raise ArgError

    while keys:
      key = keys.pop(0)
      if key == 'help':
        print help_msg
        raise ArgError

      var = aliases.get(key, key)
      if var not in defaults:
        print 'oops what is %r ?' % var
        raise ArgError


      dval = defaults[var]
      if isinstance(dval, bool):
        kwargs[var] = True
        continue
      elif isinstance(dval, int):
        if not keys and params:
          nextparam = params[0]
          if not nextparam.startswith('--') or \
              nextparams.startswith('-'):
                try:
                  val = int(nextparam)
                  kwargs[var] = val
                  params.pop(0)
                  continue

                except:
                  pass

        val = kwargs.get(var, dval)

        val +=1 
        kwargs[var] = val
        continue


      if keys or not params and dval is None:
        print 'argument %r (%r) requires value' % (key, dval)
        raise ArgError

      val = params.pop(0) if params else dval
      if isinstance(dval, list):
        val_list = kwargs.get(var) or []
        val_list.append(val)
        kwargs[var] = val_list
        continue

      kwargs[var] = val

  for arg, val in zip(positional, args):
    kwargs.pop(arg, None)

  return args, kwargs

def command(*args, **opts):

  def command(f):
    @wraps(f)
    def command(*args):
      import sys

      try:
        parsed, parsed_kwargs = parse_args(f, *args, **opts)
      except ArgError:
        sys.exit(1)

      return f(*parsed, **parsed_kwargs)

    return command

  if len(args) == 1 and not opts and callable(args[0]):
    return command(args[0])

  return command

