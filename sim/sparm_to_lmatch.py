#!/usr/bin/python3

# This program is run as:
# ./sparms_to_lmatch [-rect] <freq> <sparm file>
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
import math
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

print(f'{freq/1e6} MHz')
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

def imp_to_part_string(x, freq):
    if x < 0:
        v = 1. / (2 * math.pi * freq * -x)
        if v < 1e-12:
            vs = "%5.2ffF" % (v * 1e15)
        elif v < 1e-9:
            vs = "%5.2fpF" % (v * 1e12)
        elif v < 1e-6:
            vs = "%5.2fnF" % (v * 1e9)
        elif v < 1e-3:
            vs = "%5.2fuF" % (v * 1e6)
        elif v < 1.:
            vs = "%5.2fmF" % (v * 1e3)
        else:
            vs = "%5.2fF" % (v)
            pass
        return vs        

    v = x / (2 * math.pi * freq)
    if v < 1e-9:
        vs = "%5.2fpH" % (v * 1e12)
    elif v < 1e-6:
        vs = "%5.2fnH" % (v * 1e9)
    elif v < 1e-3:
        vs = "%5.2fuH" % (v * 1e6)
    elif v < 1.:
        vs = "%5.2fmH" % (v * 1e3)
    else:
        vs = "%5.2fH" % (v)
        pass
    return vs

# Calculate an L match based upon Ra, Zb, and the frequency.  The "m"
# parameter tells which particular match to choose, it can be -1 or 1.
# This math behind this is documented in Calculating_L_Match in this
# directory.
#
# This returns a tuple with the the impedance and a string value of the
# component required to move from the higher resistance to the lower,
# then the same for the component to move to the final value.  The
# last item in the tuple is the form of the match, type 1 or type 2,
# per the document.
def calc_l_match(za, zb, freq, m):
    # This calculation only works moving from a higher real resistance
    # to a lower one.  If we have the other way, we have to flip
    # everything around (including the order of components in the L
    # match) and calculate a little differently.
    if za.real < zb.real:
        zbr = zb.real
        zbi = zb.imag
        z1r = za.real
        zai = za.imag
        mtype = 2
    else:
        zbr = za.real
        zbi = za.imag
        z1r = zb.real
        zai = zb.imag
        mtype = 1
        pass

    # Calculate the intermediate value, Z1, between the starting place
    # and the ending place, just like you do on a Smith Chart.

    # We want the real part of the impedance of the intermediate value
    # to be the same as the real part of the impedance for the final
    # value, so we substituted than in above.  Now calculate the
    # imaginary part.
    z1i = m * math.sqrt((z1r * zbr**2 - z1r**2 * zbr + z1r * zbi**2) / zbr)

    # Now that we have the imaginary value, we can plug in to find the
    # impedance of the part required to do the move.
    x1 = ((-z1i**2 * zbi + z1i * zbi**2 + zbr**2 * z1i - z1r**2 * zbi) /
          ((z1i - zbi) ** 2 + (zbr - z1r) ** 2))

    # Moving from Z1 to the final value only requires an imaginary
    # part change, the real part is the same.
    if mtype == 1:
        x2 = -z1i - zai
    else:
        x2 = zai - z1i
        pass

    v1 = imp_to_part_string(x1, freq)
    v2 = imp_to_part_string(x2, freq)

    return (x1, v1, x2, v2, mtype)

def print_l_match_out(mtype, za, zb, v1, v2):
    if mtype == 2:
        print("                                %8s                       " % (v2))
        print("   +--------------------+--------OOOO---------+            ")
        print("   |                    |         X2          |            ")
        print("   O Zb                 O X1                  O Za         ")
        print("   O %-7.2f + j%-7.2f O %-8s            O %-7.2f + j%-7.2f   "
              % (zb.real, zb.imag, v1, za.real, za.imag))
        print("   O                    O                     O            ")
        print("   |                    |                     |            ")
        print("   v                    v                     v            ")
    else:
        print("             %8s                                        " % (v2))
        print("   +----------OOOO----------+---------------+               ")
        print("   |           X2           |               |               ")
        print("   O Zb                     O X1            O Za            ")
        print("   O %-7.2f + j%-7.2f     O %-8s      O %-7.2f + j%-7.2f "
              % (zb.real, zb.imag, v1, za.real, za.imag))
        print("   O                        O               O               ")
        print("   |                        |               |               ")
        print("   v                        v               v               ")
        pass
    return

def print_l_match_in(mtype, za, zb, v1, v2):
    if mtype == 2:
        print("   %-7.2f + j%-7.2f   %8s                                    "
              % (za.real, za.imag, v2))
        print("   +---OOOO--------------OOOO--+---------------+                  ")
        print("   |    Za                X2   |               |                  ")
        print("   |                           O X1            O Zb               ")
        print("  / \\                          O %-8s      O %5.2f + j%5.2f   "
              % (v1, zb.real, zb.imag))
        print("  \\ /                          O               O                  ")
        print("   |                           |               |                  ")
        print("   v                           v               v                  ")
    else:
        print("   %-7.2f + j%-7.2f        %8s                                  "
              % (za.real, za.imag, v2))
        print("   +---OOOO----------+--------OOOO---------+                      ")
        print("   |    Za           |         X2          |                      ")
        print("   |                 O X1                  O Zb                   ")
        print("  / \\                O %-8s            O %5.2f + j%5.2f       "
              % (v1, zb.real, zb.imag))
        print("  \\ /                O                     O                      ")
        print("   |                 |                     |                      ")
        print("   v                 v                     v                      ")
        pass
    return

def print_l_match(mtype, za, zb, v1, v2, out = False):
    if out:
        print_l_match_out(mtype, za, zb, v1, v2)
    else:
        print_l_match_in(mtype, za, zb, v1, v2)
        pass
    return

print(f' Zin: {zin}')
(x1, v1, x2, v2, mtype) = calc_l_match(zl, zin, freq, 1)
print('  match: type=%d x1=%f v1=%s  x2=%f v2=%s' % (mtype, x1, v1, x2, v2))
print('')
print_l_match(mtype, zl, zin, v1, v2)
print('')
(x1, v1, x2, v2, mtype) = calc_l_match(zl, zin, freq, -1)
print('  match: type=%d x1=%f v1=%s  x2=%f v2=%s' % (mtype, x1, v1, x2, v2))
print('')
print_l_match(mtype, zl, zin, v1, v2)
print('')

print(f' Zout: {zout}')
(x1, v1, x2, v2, mtype) = calc_l_match(zs, zout, freq, 1)
print('  match: type=%d x1=%f v1=%s  x2=%f v2=%s' % (mtype, x1, v1, x2, v2))
print('')
print_l_match(mtype, zl, zout, v1, v2, out = True)
print('')
(x1, v1, x2, v2, mtype) = calc_l_match(zs, zout, freq, -1)
print('  match: type=%d x1=%f v1=%s  x2=%f v2=%s' % (mtype, x1, v1, x2, v2))
print('')
print_l_match(mtype, zl, zout, v1, v2, out = True)
print('')
