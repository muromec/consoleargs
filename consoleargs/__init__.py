from functools import wraps
import inspect

class ArgError(Exception):
  pass

def positional_error(positional, args):
  delt = len(positional) - len(args)
  for arg in positional[-delt:]:
    print 'Positional argument %r not specified' %arg

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
  """ Function prints command line help information:
    - function docstring
    - list of possible params
  """
  if callable(func):
    import sys
    mod = sys.modules.get(func.__module__)
    name = mod.__file__
  else:
    name = func

  import re
  param_help = dict(re.findall(':param ([a-zA-Z_]+): (.*)\n',
      func.__doc__ or '',
      flags=re.MULTILINE))

  msg = "Usage: %(progname)s " % {"progname": name}

  kwargs = list(defaults.keys())
  for arg in positional:
    if arg in kwargs:
      msg += '[%s]' % arg.upper()
      if isinstance(defaults[arg], list):
        msg += '... '
      else:
        msg += ' '

      kwargs.remove(arg)
    else:
      msg += '%s ' % arg.upper()

  if kwargs:
    msg += '[OPTIONS]'

  msg += '\n\n'

  for arg in positional:
    if arg in param_help:
      msg += '%s:\t%s\n' % (arg.upper(), param_help[arg])

  msg += '\nOptions:\n'

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

    if arg in param_help:
      msg += '\t'
      msg += param_help.get(arg)

    msg += '\n'

  return msg

def parse_args(f, *args, **opts):
  def print_help():
    print build_help(f, positional, defaults, aliases)

  spec = inspect.getargspec(f)
  positional, defaults, _defaults = list(spec.args), {}, list(spec.defaults or [])
  _positional = opts.get('positional') or []
  all_help = opts.get('all_help', True)
  required = positional[:]

  while _defaults:
    v = _defaults.pop()
    k = positional[-1]

    if k not in _positional:
      positional.pop()

    required.pop()

    defaults[k] = v

  aliases = build_aliases(defaults)

  if args and args[0] in ['--help', '-h']:
    print_help()
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
    elif all_help and param == 'help':
      print_help()
      raise ArgError

    elif len(positional) - len(args) > 1:
      args.append(param)
      continue
    elif len(positional) - len(args) == 1:
      dval = defaults.get(positional[-1])
      if isinstance(dval, list):
        args.append([param])
      else:
        args.append(param)

      continue
    elif args and len(positional) == len(args) \
        and isinstance(args[-1], list):
          args[-1].append(param)
          continue
    elif spec.varargs:
      args.append(param)
      continue
    else:
      print 'invalid param', param
      raise ArgError

    while keys:
      key = keys.pop(0)
      if all_help and key == 'help':
        print_help()
        raise ArgError

      if '=' in key:
        key,_val = key.split('=')
      else:
        _val = None

      var = aliases.get(key, key)
      if var not in defaults:
        if spec.varargs:
            args.append(param)
            continue

        print 'oops what is %r ?' % var
        raise ArgError


      dval = defaults[var]
      if isinstance(dval, bool):
        kwargs[var] = True
        continue
      elif isinstance(dval, int):
        if not keys and params:
          nextparam = params[0]
          if not nextparam.startswith('--'):
            try:
              if nextparam[:2].lower() == '0x':
                val = int(nextparam, 16)
              else:
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


      if keys or not params and dval is None and _val is None:
        print 'argument %r (%r) requires value' % (key, dval)
        raise ArgError

      val = _val if _val is not None else params.pop(0) if params else dval
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
      argv = opts.get('argv', True)
      if not args and argv:
          first = 1 if argv is True else argv
          last = None
          if isinstance(argv, (list, tuple)) and len(argv) == 2:
              first, last = argv

          args = sys.argv[first:last]

      try:
        parsed, parsed_kwargs = parse_args(f, *args, **opts)
      except ArgError:
        sys.exit(1)

      return f(*parsed, **parsed_kwargs)

    return command

  if len(args) == 1 and not opts and callable(args[0]):
    return command(args[0])

  return command


