#!/usr/bin/python3

# This program is run as:
# ./calc_sparms [-rect] <freq> <sparm file>
#
# It parses through the sparm file to find where the given frequency
# is located then interpolates between the two frequencies around the
# given frequency.  It uses that as the sparms and calculates zin and
# zout.
#
# By default data in the file is in the format:
#  <freq> <s11> <s21> <s12> <s22>
# where each S-parameters is two numbers, the magnitude and angle.
#
# if -rect is specified, then the S-parameters are in the form <real> <imag>

import sys
import numpy as np
from two_port_conversions import *

rect = False
verbose = False

def get_complex(i, n):
    return float(i[n]) + 1j * float(i[n+1])

def get_sparm(i):
    s11 = get_complex(i, 1)
    s21 = get_complex(i, 3)
    s12 = get_complex(i, 5)
    s22 = get_complex(i, 7)
    return np.array([ [ s11, s12 ], [ s21, s22 ]])
    
def get_sparms(freq, fname):
    f = open(fname, "r")
    last_line = None
    # Hunt for the proper S-Parameters
    for i in f:
        if not i[0].isdigit():
            continue
        i = i.split()
        f2 = float(i[0])
        if f2 < freq:
            last_line = i
            continue
        if len(last_line) < 9:
            print("line not valid: " + ' '.join(last_line))
            raise Exception("Invalid S-param file")
        if len(i) < 9:
            print("line not valid: " + ' '.join(i))
            raise Exception("Invalid S-param file")

        # The last one was <freq, current is >=freq
        f1 = float(last_line[0])
        return [ f1, get_sparm(last_line), f2, get_sparm(i) ]
        pass
    raise Exception("No frequency found")

args = sys.argv[1:]

while len(args) > 1:
    if args[0][0] != '-':
        break
    if args[0] == "-rect":
        rect = True
    elif args[0] == "-verbose":
        verbose = True
    else:
        raise Exception("Invalid parameter: " + args[0])
    del(args[0])
    pass

if len(args) < 2:
    print("Two parameters: [-rect] <freq> <file>")
    raise Exception("Not enough parameters")

freq = float(args[0])

p = get_sparms(freq, args[1])

if rect:
    p[1] = rect_to_db_degrees(p[1])
    p[3] = rect_to_db_degrees(p[3])
    pass

# Interpolate those to the frequency
sdb = interp_matrix(p[1], p[0], p[3], p[2], freq)

# Now convert those to rectangular coordinates for use in the conversions
s = matrix_db_degrees_to_rect(sdb)

# Convert to a Z matrix
z = s_to_z(s, z0_50)

print(f'{freq} MHz')
if verbose:
    print(f'Sdb_{p[0]}: \n{p[1]}\n')
    print(f'Sdb_{p[2]}: \n{p[3]}\n')
    print(f'S_{freq}: \n{s}\n')
    print(f'Z_{freq}: \n{z}\n')
    pass

zl = 50
zs = 50

# Now calculate zin and zout from the z matrix.
zin = z_to_zin(z, zl)
zout = z_to_zout(z, zs)

print(f' Zin: {zin}')
print(f' Zout: {zout}')
