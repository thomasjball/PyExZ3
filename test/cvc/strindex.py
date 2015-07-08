from symbolic.args import symbolic


@symbolic(s="foobar")
def strindex(s):
    """Test case does not currently test negative indexes.
    It is also currently unclear how we want to handle concrete
    executions that raise errors. Currently the error stops
    execution and prevents a branch predicate from forming."""
    if s[4] == 'Q':
        return 0
    else:
        return 1


def expected_result():
    return [0, 1]
