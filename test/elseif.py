# vim: set expandtab ts=4 sw=4:
#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
# To this file contributed: Peter Peresini
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   -  Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   -  Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   -  Neither the names of the contributors, nor their associated universities or
#      organizations may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Test if engine explores all paths

def elseif(in1):
    if in1 ==  0:
        return 0
    elif in1 == 1:
        return 1
    elif in1 == 2:
        return 2
    elif in1 == 3:
        return 3
    elif in1 == 4:
        return 4
    elif in1 == 5:
        return 5
    elif in1 == 6:
        return 6
    elif in1 == 7:
        return 7
    elif in1 == 8:
        return 8
    else:
        return 9

    return 10

