from symbolic.args import symbolic


@symbolic(s="bar")
def strreplace(s):
    if "faa" == s.replace("o", "a"):
        return 0
    else:
        return 1


def expected_result_set():
    return {0, 1}
