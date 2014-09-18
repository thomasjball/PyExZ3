# Copyright: see copyright.txt

# Test if engine explores all paths

from lib.se_dict import SymbolicDictionary

def dictionary(in1):
    d = SymbolicDictionary({})
    d[3] = 10

    if d.has_key(in1):
        return 1
    else:
        return 2

def expected_result():
	return [1,2]