# Check if SymbolicInteger is a subtype of `int' modulo concolic execution.
#
# To run:
# $ python sym_exec.py examples/symbolic_int_subtype.py

from inspect import signature

from symbolic.symbolic_types.symbolic_int import SymbolicInteger

# Collect integer methods to test.
INT_FUNCS = []
for fname in dir(int):
  # TODO for some functions signature lookup fails, maybe hardcode arity
  try:
    if fname in ('__delattr__', '__getattribute__', '__setattr__',
                 '__new__', '__init__'):
      continue
    INT_FUNCS.append((fname, len(signature(getattr(int, fname)).parameters)))
  except:
    pass

# NOTE Uncomment this to have a restricted set of (correctly modelled) functions
# INT_FUNCS = [ ('__add__', 2), ('__sub__', 2), ('__and__', 2), ('__or__', 2) ]

def symbolic_int_subtype(func_index, a, b, c):
  # make concolic execution branch on elements of INT_FUNCS
  if func_index in [ i for i, fname in enumerate(INT_FUNCS) if INT_FUNCS[i] ]:
    name, arity = INT_FUNCS[func_index]
    print("%s/%d" % (name, arity))

    assert(0 <= arity <= 3)

    int_params = [ int(a), int(b), int(c) ]
    sym_params = [ a, b, c ]

    int_func = getattr(int, name)
    sym_func = getattr(SymbolicInteger, name)

    try:
      int_return = int_func(*int_params[:arity])
    except ValueError as e:
      int_return = e
    except ZeroDivisionError as e:
      int_return = e

    try:
      sym_return = sym_func(*sym_params[:arity])
    except ValueError as e:
      sym_return = e
    except ZeroDivisionError as e:
      sym_return = e

    same = ((isinstance(int_return, Exception) and
             isinstance(sym_return, Exception) and
             type(int_return) == type(sym_return)
            ) or int_return == sym_return)

    if not same:
      s = ("\nint %s(%s): %r,\nsym %s(%s): %r" %
           (name, ','.join(str(i) for i in int_params), int_return,
           name, ','.join(str(i) for i in sym_params), sym_return))
      raise Exception(s)

    return (name, same)

  else:
    return "OUTSIDE"

# TODO Implement oracle.
#      How to predict the number of paths for a given int method?
