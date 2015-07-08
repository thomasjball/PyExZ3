from symbolic.args import symbolic


@symbolic(s="foo")
def stringtest(s):
    if (s == "bar"):
        return 0
    elif (s == '\\'):
        return 2
    else:
        return 1


def expected_result_set():
    return {0, 1, 2}
