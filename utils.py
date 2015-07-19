# Copyright: see copyright.txt

import sys
import traceback


def traceback():
    stack = traceback.format_stack()
    rest = stack[:-2]
    return "\n" + "".join(rest)


def crash(msg):
    # stack = _traceback()
    print(msg)
    sys.exit(-1)
