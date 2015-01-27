from symbolic.args import *

class Foo():
    def __init__(self, var):
        self.var = var

    def __len__(self):
        return self.var

@symbolic(a=0)
def len_test(a):
    f = Foo(a)
    if len(f) == 2:
        return 1
    else:
        return 0

def expected_result():
    return [0, 1]

