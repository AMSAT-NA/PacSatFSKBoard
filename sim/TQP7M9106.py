import numpy as np
from two_port_conversions import *

# Qorvo TQP7M9106 at 435MHz (interpolated)

# S-parameters as given in the data sheet, db and angle, 403MHz and 453MHz
#
# This is not correct, but it shows how to interpolate values.  The
# value from the S-Parameters what exactly what we needed.
#s403db = np.array([[ -3.984314e-001 + 1j * -1.014494e+002,
#                     -4.224903e+001 + 1j *  5.146908e+001],
#                   [  2.086655e+001 + 1j *  1.505175e+002,
#	             -2.063475e+000 + 1j * -1.549018e+002]])
#s453db = np.array([[ -4.216216e-001 + 1j * -1.083204e+002,
#	             -4.233332e+001 + 1j *  3.963127e+001],
#                   [  2.031235e+001 + 1j *  1.472462e+002,
#	             -2.094049e+000 + 1j * -1.570179e+002]])
# Interpolate those to 435MHz
#sdb435db = interp_matrix(s403db, 403, s453db, 453, 435)

# 435,286,950Hz
s435db = np.array([[ -5.639662e-001 + 1j * -1.775963e+002,
	             -4.030942e+001 + 1j *  4.379921e+000 ],
	           [  1.088140e+001 + 1j *  1.205044e+002,
	             -1.614764e+000 + 1j * -1.788264e+002]])

# Interpolate those to 435MHz
sdb = s435db

# Now convert those to rectangular coordinates for use in the conversions
s = matrix_db_degrees_to_rect(sdb)

# Convert to a Z matrix
z = s_to_z(s, z0_50)

print('435 MHz')
print(f'Sdb_435: \n{sdb}\n')
print(f'S_435: \n{s}\n')
print(f'Z_435: \n{z}\n')

zl = 50
zs = 50

# Now calculate zin and zout from the z matrix.
zin = z_to_zin(z, zl)
zout = z_to_zout(z, zs)

print(f'Zin: {zin}')
print(f'Zout: {zout}')
print("\n")
