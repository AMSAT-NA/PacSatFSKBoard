#!/usr/bin/python3

# Convert Z0_even and Z0_odd from a field solver into the input
# impedance of each leg: Z0 and the coupling (k) in dB.
# It also prints the wavelength in the medium of the given length.
# The wavelength is used to calculate the coupling.
#
# Parameters are: Z0e Z0o <length in mm> <freq in MHz> <Er>
#
# length is the length of the coupled section.
#
# frequency is required to calculate the wavelength
#
# Er (permativity of the material) is also required to calculate the
# wavelengh.

import sys
from math import *
import numpy as np

args = sys.argv[1:]

if len(args) < 5:
    print("Input is Z0e Z0o <length in mm> <freq in MHz> <Er>")
    sys.exit(1)
    pass

Z0e = float(args[0])
Z0o = float(args[1])
length = float(args[2]) / 1000
freq = float(args[3]) * 1e6
Er = float(args[4])

Z0 = sqrt(Z0e * Z0o)

# Coupling coefficient
Co = (Z0e - Z0o) / (Z0e + Z0o)

wavelen = 2.998e8 / (freq * sqrt(Er))

Om = 2 * pi * length / wavelen

S31 = Co * sin(Om) / sqrt(1 - pow(Co, 2) * pow(cos(Om), 2))

k = 20 * log10(fabs(S31))

print("wavelen = %.2fmm" % (wavelen * 1000 + .005))
print("Z0 = %.2f" % (Z0 + .005))
print("coupling = %.2fdB" % (k + .005))

