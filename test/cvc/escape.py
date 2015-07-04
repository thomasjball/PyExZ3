from symbolic.args import *

@symbolic(string="foo")
def escape(string):
    if string and '\\' not in string and string.find(':') > 0:
        return 0
    else:
        return 1

def expected_result_set():
    return {0, 1}
