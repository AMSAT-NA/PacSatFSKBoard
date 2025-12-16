import numpy as np
from two_port_conversions import *

# Qorvo TQP7M9106 at 435MHz (interpolated)

# S-parameters as given in the data sheet, db and angle, 403MHz and 453MHz
s403db = np.array([[ -3.984314e-001 + 1j * -1.014494e+002,
                     -4.224903e+001 + 1j *  5.146908e+001],
                   [  2.086655e+001 + 1j *  1.505175e+002,
	             -2.063475e+000 + 1j * -1.549018e+002]])
s453db = np.array([[ -4.216216e-001 + 1j * -1.083204e+002,
	             -4.233332e+001 + 1j *  3.963127e+001],
                   [  2.031235e+001 + 1j *  1.472462e+002,
	             -2.094049e+000 + 1j * -1.570179e+002]])

# Interpolate those to 435MHz
sdb = interp_matrix(s403db, 403, s453db, 453, 435)

# Now convert those to rectangular coordinates for use in the conversions
s = matrix_db_degrees_to_rect(sdb)

# Convert to a Z matrix
z = s_to_z(s, z0_50)

print('435 MHz')
print(f'Sdb_403: \n{s403db}\n')
print(f'Sdb_453: \n{s453db}\n')
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
