# Given frequency, bandwidth, input impedance, and output impedance,
# this program calculates the component values for a Pi filter for the
# given parameters.  It spits out some spice code for this.

import sys
import numpy as np


freq = float(sys.argv[1])
bw = float(sys.argv[2])
rin = float(sys.argv[3])
rout = float(sys.argv[4])

q = freq / bw
Xc1 = rout / q
Xc2 = rin * np.sqrt((rout / rin) / (q * q + 1 - (rout / rin)))
Xl = (q * rout + (rout * rin / Xc2)) / (q * q + 1)

c1 = 1. / (2 * np.pi * freq * Xc1)
c2 = 1. / (2 * np.pi * freq * Xc2)
l = Xl / (2 * np.pi * freq)

print("* Freq = %f  bw = %f  Rin = %f  Rout = %f" % (freq, bw, rin, rout))
print("* Q = %f  Xc1 = %f  Xc2 = %f  Xl = %f" % (q, Xc1, Xc2, Xl))
print("C2 a1 0 %fp" % (c2 * 1e12))
print("L1 a1 m1 %fn" % (l * 1e9))
print("RL1 m1 a2 %f" % .3)
print("CL1 a1 a2 %fp" % .048)
print("C1 a2 0 %fp" % (c1 * 1e12))
