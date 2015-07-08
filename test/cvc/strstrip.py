from symbolic.args import symbolic


@symbolic(s="foo")
def strstrip(s):
    if " " in s and "abc" == s.strip():
        return 0
    return 1


def expected_result_set():
    return {0, 1}
