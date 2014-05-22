#!/bin/bash

for t in many_branches shallow_branches loop logical_op elif dictionary count_packets expressions; do
	./sym_exec.py -q -l /dev/null test $t
done

