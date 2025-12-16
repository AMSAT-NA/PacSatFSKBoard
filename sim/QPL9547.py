import numpy as np
from two_port_conversions import *

# Qorvo QPL9547 at 145MHz (interpolated)

# S-parameters as given in the data sheet, db and angle, 100MHz and
# 150MHz.  The S-parameter file is in rectangular form, even though it
# says mag/angle.
s100 = np.array([[  5.794645e-001 + 1j * -1.408821e-001,
                   -2.877069e+001 + 1j *  6.625641e+000],
                 [  1.525606e-002 + 1j *  2.369791e-003,
                    2.672137e-001 + 1j * -1.273641e-002]])
s150 = np.array([[  5.555961e-001 + 1j * -1.902591e-001,
                   -2.759329e+001 + 1j *  9.165064e+000],
                 [  1.530945e-002 + 1j *  2.830682e-003,
                    2.693962e-001 + 1j * -9.745223e-003 ]])

# Convert to DB/Angle so we can interpolate.
s100db = rect_to_db_degrees(s100)
s150db = rect_to_db_degrees(s150)

# Interpolate those to 145MHz
sdb = interp_matrix(s100db, 100, s150db, 150, 145)

# Now convert those to rectangular coordinates for use in the conversions
s = matrix_db_degrees_to_rect(sdb)

# Convert to a Z matrix
z = s_to_z(s, z0_50)

print('145 MHz')
print(f'Sdb_100: \n{s100db}\n')
print(f'Sdb_150: \n{s150db}\n')
print(f'Sdb_145: \n{sdb}\n')
print(f'S_145: \n{s}\n')
print(f'Z_145: \n{z}\n')

zl = 50
zs = 50

# Now calculate zin and zout from the z matrix.
zin = z_to_zin(z, zl)
zout = z_to_zout(z, zs)

print(f'Zin: {zin}')
print(f'Zout: {zout}')
print("\n")
