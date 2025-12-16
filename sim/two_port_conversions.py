# IEEE TRANSACTIONS ON MICROWAVE THEORY AND TECHNIQUES. VOL 42, NO 2. FEBRUARY 1994
# Conversions Between S, Z, Y, h, ABCD, and T Parameters which are Valid for Complex Source and Load Impedances
# Dean A. Frickey, Member, EEE

# Note, the S parameter matrix is input as:
#
#  [[ S11, S12 ], [ S21, S22 ]]

# Tables I and II

# This is taken from https://www.rfcafe.com/references/electrical/s-h-y-z.htm

import numpy as np

# Convenience 50 ohm Z0
z0_50 = np.array([50,50])

def interp(v1, f1, v2, f2, f):
    """ Linearly interpolate values between frequencies.  Note that
    f1 <= f <= f2.

    :param v1: The value at f1
    :param f1: The frequency where v1 is
    :param v2: The value at f2
    :param f2: The frequency where v2 is
    :param f: The frequency to interpolate to
    """
    diff = f2 - f1
    fpos = f - f1
    return (v2 - v1) * fpos / diff + v1

def interp_matrix(m1, f1, m2, f2, f):
    """Given two matrices for something (like S parameters) at given
    frequencies, interpolate them to a frequency between the two given
    frequencies.  Note that f1 <= f <= f2.
    
    :param m1: The matrix at f1
    :param f1: The frequency where m1 is
    :param m2: The value at f2
    :param f2: The frequency where m2 is
    :param f: The frequency to interpolate to

    """
    m11 = (interp(m1[0,0].real, f1, m2[0,0].real, f2, f)
           + 1j * interp(m1[0,0].imag, f1, m2[0,0].imag, f2, f))

    m12 = (interp(m1[0,1].real, f1, m2[0,1].real, f2, f)
           + 1j * interp(m1[0,1].imag, f1, m2[0,1].imag, f2, f))

    m21 = (interp(m1[1,0].real, f1, m2[1,0].real, f2, f)
           + 1j * interp(m1[1,0].imag, f1, m2[1,0].imag, f2, f))

    m22 = (interp(m1[1,1].real, f1, m2[1,1].real, f2, f)
           + 1j * interp(m1[1,1].imag, f1, m2[1,1].imag, f2, f))

    return np.array([[m11, m12],[m21,m22]])

def db_degrees_to_rect(s):
    """ Convert a single dB/degrees value to rectangular form

    :param s: The complex number in the form (value in dB, degrees)
    :return: The number converted to rectangular form
    """
    # Decibels to voltage value.
    v = 10. ** (s.real / 20)
    return v * np.exp(1j * np.radians(s.imag))

def matrix_db_degrees_to_rect(s):
    """ Matrix in dBs/degrees to rectangular form

    :param s: The matrix in dBs/degrees
    :return: The matrix in rectangular form
    """
    z = np.zeros([2,2], dtype=complex)

    z[0,0] = db_degrees_to_rect(s[0,0])
    z[0,1] = db_degrees_to_rect(s[0,1])
    z[1,0] = db_degrees_to_rect(s[1,0])
    z[1,1] = db_degrees_to_rect(s[1,1])
    return z

def rect_to_db_degrees(s):
    """ Convert a single dB/degrees value to rectangular form

    :param s: The complex number in the form (value in dB, degrees)
    :return: The number converted to rectangular form
    """
    # Decibels to voltage value.
    v = np.sqrt(s.real ** 2 + s.imag ** 2)
    vdb = np.log10(v) * 20
    ang = np.degrees(np.arctan2(s.imag, s.real))
    return vdb + 1j * ang

def matrix_rect_to_db_degrees(s):
    """ Matrix in dBs/degrees to rectangular form

    :param s: The matrix in dBs/degrees
    :return: The matrix in rectangular form
    """
    z = np.zeros([2,2], dtype=complex)

    z[0,0] = rect_to_db_degrees(s[0,0])
    z[0,1] = rect_to_db_degrees(s[0,1])
    z[1,0] = rect_to_db_degrees(s[1,0])
    z[1,1] = rect_to_db_degrees(s[1,1])
    return z

def z_to_zin(z, zload):
    """ Get the input impedance from the Z matrix and the load impedance.

    :param z: The Z matrix
    :param zload: The load impedance (ohms)
    :return: The input impedance
    """
    # Taken from https://en.wikipedia.org/wiki/Impedance_parameters
    return z[0,0] - (z[0,1] * z[1,0])/(z[1,1] + zload)

def z_to_zout(z, zsource):
    """ Get the output impedance from the Z matrix and the source impedance.

    :param z: The Z matrix
    :param zsource: The source impedance (ohms)
    :return: The output impedance
    """
    # Taken from https://en.wikipedia.org/wiki/Impedance_parameters
    return z[1,1] - (z[0,1] * z[1,0])/(z[0,0] + zsource)

def s_to_z(s, z0):
    """ Scattering (S) to Impedance (Z)

    :param s: The scattering matrix.
    :param z0: The port impedances (Ohms).
    :return: The impedance matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    z = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = (1 - s[0,0]) * (1 - s[1,1]) - s[0,1] * s[1,0]

    # Calculate the numerators
    z[0,0] = (z0c[0] + s[0,0] * z0[0]) * (1 - s[1,1]) + s[0,1] * s[1,0] * z0[0]
    z[0,1] = 2 * s[0,1] * np.sqrt(z0[0].real * z0[1].real)
    z[1,0] = 2 * s[1,0] * np.sqrt(z0[0].real * z0[1].real)
    z[1,1] = (1 - s[0,0]) * (z0c[1] + s[1,1] * z0[1]) + s[0,1] * s[1,0] * z0[1]

    # Return the conversion
    return z / denominator


def z_to_s(z, z0):
    """ Impedance (Z) to Scattering (S)

    :param z: The impedance matrix.
    :param z0: The port impedances (Ohms).
    :return: The scattering matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    s = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = (z[0,0] + z0[0]) * (z[1,1] + z0[1]) - z[0,1] * z[1,0]

    # Calculate the numerators
    s[0,0] = (z[0,0] - z0c[0]) * (z[1,1] + z0[1]) - z[0,1] * z[1,0]
    s[0,1] = 2 * z[0,1] * np.sqrt(z0[0].real * z0[1].real)
    s[1,0] = 2 * z[1,0] * np.sqrt(z0[0].real * z0[1].real)
    s[1,1] = (z[0,0] + z0[0]) * (z[1,1] - z0c[1]) - z[0,1] * z[1,0]

    # Return the conversion
    return s / denominator


def s_to_y(s, z0):
    """ Scattering (S) to Admittance (Y)

    :param s: The scattering matrix.
    :param z0: The port impedances (Ohms).
    :return: The admittance matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    y = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = (z0c[0] + s[0,0] * z0[0]) * (z0c[1] + s[1,1] * z0[1]) - s[0,1] * s[1,0] * z0[0] * z0[1]

    # Calculate the numerators
    y[0,0] = (1 - s[0,0]) * (z0c[1] + s[1,1] * z0[1]) + s[0,1] * s[1,0] * z0[1]
    y[0,1] = -2 * s[0,1] * np.sqrt(z0[0].real * z0[1].real)
    y[1,0] = -2 * s[1,0] * np.sqrt(z0[0].real * z0[1].real)
    y[1,1] = (z0c[0] + s[0,0] * z0[0]) * (1 - s[1,1]) + s[0,1] * s[1,0] * z0[0]

    # Return the conversion
    return y / denominator


def y_to_s(y, z0):
    """ Admittance (Y) to Scattering (S)

    :param y: The admittance matrix.
    :param z0: The port impedances (Ohms).
    :return: The scattering matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    s = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = (1 + y[0,0] * z0[0]) * (1 + y[1,1] * z0[1]) - y[0,1] * y[1,0] * z0[0] * z0[1]

    # Calculate the numerators
    s[0,0] = (1 - y[0,0] * z0c[0]) * (1 + y[1,1] * z0[1]) + y[0,1] * y[1,0] * z0c[0] * z0[1]
    s[0,1] = -2 * y[0,1] * np.sqrt(z0[0].real * z0[1].real)
    s[1,0] = -2 * y[1,0] * np.sqrt(z0[0].real * z0[1].real)
    s[1,1] = (1 + y[0,0] * z0[0]) * (1 - y[1,1] * z0c[1]) + y[0,1] * y[1,0] * z0[0] * z0c[1]

    # Return the conversion
    return s / denominator


def s_to_h(s, z0):
    """ Scattering (S) to Hybrid (H)

    :param s: The scattering matrix.
    :param z0: The port impedances (Ohms).
    :return: The hybrid matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    h = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = (1 - s[0,0]) * (z0c[1] + s[1,1] * z0[1]) + s[0,1] * s[1,0] * z0[1]

    # Calculate the numerators
    h[0,0] = (z0c[0] + s[0,0] * z0[0]) * (z0c[1] + s[1,1] * z0[1]) - s[0,1] * s[1,0] * z0[0] * z0[1]
    h[0,1] = 2 * s[0,1] * np.sqrt(z0[0].real * z0[1].real)
    h[1,0] = -2 * s[1,0] * np.sqrt(z0[0].real * z0[1].real)
    h[1,1] = (1 - s[0,0]) * (1 - s[1,1]) - s[0,1] * s[1,0]

    # Return the conversion
    return h / denominator


def h_to_s(h, z0):
    """ Hybrid (H) to Scattering (S)

    :param h: The hybrid matrix.
    :param z0: The port impedances (Ohms).
    :return: The scattering matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    s = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = (z0[0] + h[0,0]) * (1 + h[1,1] * z0[1]) - h[0,1] * h[1,0] * z0[1]

    # Calculate the numerators
    s[0,0] = (h[0,0] - z0c[0]) * (1 + h[1,1] * z0[1]) - h[0,1] * h[1,0] * z0[1]
    s[0,1] = 2 * h[0,1] * np.sqrt(z0[0].real * z0[1].real)
    s[1,0] = -2 * h[1,0] * np.sqrt(z0[0].real * z0[1].real)
    s[1,1] = (z0[0] + h[0,0]) * (1 - h[1,1] * z0c[1]) + h[0,1] * h[1,0] * z0c[1]

    # Return the conversion
    return s / denominator


def s_to_abcd(s, z0):
    """ Scattering to Chain (ABCD)

    :param s: The scattering matrix.
    :param z0: The port impedances (Ohms).
    :return: The chain matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    ans = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = 2 * s[1,0] * np.sqrt(z0[0].real * z0[1].real)

    # Calculate the numerators
    ans[0,0] = (z0c[0] + s[0,0] * z0[0]) * (1 - s[1,1]) + s[0,1] * s[1,0] * z0[0]
    ans[0,1] = (z0c[0] + s[0,0] * z0[0]) * (z0c[1] + s[1,1] * z0[1]) - s[0,1] * s[1,0] * z0[0] * z0[1]
    ans[1,0] = (1 - s[0,0]) * (1 - s[1,1]) - s[0,1] * s[1,0]
    ans[1,1] = (1 - s[0,0]) * (z0c[1] + s[1,1] * z0[1]) + s[0,1] * s[1,0] * z0[1]

    # Return the conversion
    return ans / denominator


def abcd_to_s(abcd, z0):
    """ Chain (ABCD) to Scattering (S)

    :param abcd: The chain matrix.
    :param z0: The port impedances (Ohms).
    :return: The scattering matrix.
    """
    # Break out the components
    A = abcd[0,0]
    B = abcd[0,1]
    C = abcd[1,0]
    D = abcd[1,1]

    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    s = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = A * z0[1] + B + C * z0[0] * z0[1] + D * z0[0]

    # Calculate the numerators
    s[0,0] = A * z0[1] + B - C * z0c[0] * z0[1] - D * z0c[0]
    s[0,1] = 2 * (A * D - B * C) * np.sqrt(z0[0].real * z0[1].real)
    s[1,0] = 2 * np.sqrt(z0[0].real * z0[1].real)
    s[1,1] = -A * z0c[1] + B - C * z0[0] * z0c[1] + D * z0[0]

    # Return the conversion
    return s / denominator


def t_to_z(t, z0):
    """ Chain Transfer (T) to Impedance (Z)

    :param t: The chain transfer matrix.
    :param z0: The port impedances (Ohms).
    :return: The impedance matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    z = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = t[0,0] + t[0,1] - t[1,0] - t[1,1]

    # Calculate the numerators
    z[0,0] = z0c[0] * (t[0,0] + t[0,1]) + z0[0] * (t[1,0] + t[1,1])
    z[0,1] = 2 * np.sqrt(z0[0].real * z0[1].real) * (t[0,0] * t[1,1] - t[0,1] * t[1,0])
    z[1,0] = 2 * np.sqrt(z0[0].real * z0[1].real)
    z[1,1] = z0c[1] * (t[0,0] - t[1,0]) - z0[1] * (t[0,1] - t[1,1])

    # Return the conversion
    return z / denominator


def z_to_t(z, z0):
    """ Impedance (Z) to Chain Transfer (T)

    :param z: The impedance matrix.
    :param z0: The port impedances (Ohms).
    :return: The chain transfer matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    t = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = 2 * z[1,0] * np.sqrt(z0[0].real * z0[1].real)

    # Calculate the numerators
    t[0,0] = (z[0,0] + z0[0]) * (z[1,1] + z0[1]) - z[0,1] * z[1,0]
    t[0,1] = (z[0,0] + z0[0]) * (z0c[1] - z[1,1]) + z[0,1] * z[1,0]
    t[1,0] = (z[0,0] - z0c[0]) * (z[1,1] + z0[1]) - z[0,1] * z[1,0]
    t[1,1] = (z0c[0] - z[0,0]) * (z[1,1] - z0c[1]) + z[0,1] * z[1,0]

    # Return the conversion
    return t / denominator


def t_to_y(t, z0):
    """ Chain Transfer (T) to Admittance (Y)

    :param t: The chain transfer matrix.
    :param z0: The port impedances (Ohms).
    :return: The admittance matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    y = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = t[0,0] * z0c[0] * z0c[1] - t[0,1] * z0c[0] * z0[1] + t[1,0] * z0[0] * z0c[1] - t[1,1] * z0[0] * z0[1]

    # Calculate the numerators
    y[0,0] = z0c[1] * (t[0,0] - t[1,0]) - z0[1] * (t[0,1] - t[1,1])
    y[0,1] = -2 * np.sqrt(z0[0].real * z0[1].real) * (t[0,0] * t[1,1] - t[0,1] * t[1,0])
    y[1,0] = -2 * np.sqrt(z0[0].real * z0[1].real)
    y[1,1] = z0c[0] * (t[0,0] + t[0,1]) + z0[0] * (t[1,0] + t[1,1])

    # Return the conversion
    return y / denominator


def y_to_t(y, z0):
    """ Admittance (Y) to Chain Transfer (T)

    :param y: The admittance matrix.
    :param z0: The port impedances (Ohms).
    :return: The chain transfer matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    t = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = 2 * y[1,0] * np.sqrt(z0[0].real * z0[1].real)

    # Calculate the numerators
    t[0,0] = (-1 - y[0,0] * z0[0]) * (1 + y[1,1] * z0[1]) + y[0,1] * y[1,0] * z0[0] * z0[1]
    t[0,1] = (1 + y[0,0] * z0[0]) * (1 - y[1,1] * z0c[1]) + y[0,1] * y[1,0] * z0[0] * z0c[1]
    t[1,0] = (y[0,0] * z0c[0] - 1) * (1 + y[1,1] * z0[1]) - y[0,1] * y[1,0] * z0c[0] * z0[1]
    t[1,1] = (1 - y[0,0] * z0c[0]) * (1 - y[1,1] * z0c[1]) - y[0,1] * y[1,0] * z0c[0] * z0c[1]

    # Return the conversion
    return t / denominator


def t_to_h(t, z0):
    """ Chain Transfer (T) to Hybrid (H)

    :param t: The chain transfer matrix.
    :param z0: The port impedances (Ohms).
    :return: The hybrid matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    h = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = z0c[1] * (t[0,0] - t[1,0]) - z0[1] * (t[0,1] - t[1,1])

    # Calculate the numerators
    h[0,0] = z0c[1]*(t[0,0] * z0c[0] + t[1,0] * z0[0]) - z0[1] * (t[0,1] * z0c[0] + t[1,1] * z0[0])
    h[0,1] = 2 * np.sqrt(z0[0].real * z0[1].real) * (t[0,0] * t[1,1] - t[0,1] * t[1,0])
    h[1,0] = -2 * np.sqrt(z0[0].real * z0[1].real)
    h[1,1] = t[0,0] + t[0,1] - t[1,0] - t[1,1]

    # Return the conversion
    return h / denominator


def h_to_t(h, z0):
    """ Hybrid (H) to Chain Transfer (T)

    :param t: The hybrid matrix.
    :param z0: The port impedances (Ohms).
    :return: The chain transfer matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    t = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = 2 * h[1,0] * np.sqrt(z0[0].real * z0[1].real)

    # Calculate the numerators
    t[0,0] = (-h[0,0] - z0[0]) * (1 + h[1,1] * z0[1]) + h[0,1] * h[1,0] * z0[1]
    t[0,1] = (h[0,0] + z0[0]) * (1 - h[1,1] * z0c[1]) + h[0,1] * h[1,0] * z0c[1]
    t[1,0] = (z0c[0] - h[0,0]) * (1 + h[1,1] * z0[1]) + h[0,1] * h[1,0] * z0[1]
    t[1,1] = (h[0,0] - z0c[0]) * (1 - h[1,1] * z0c[1]) + h[0,1] * h[1,0] * z0c[1]

    # Return the conversion
    return t / denominator


def t_to_abcd(t, z0):
    """ Chain Transfer (T) to Chain (ABCD)

    :param t: The chain transfer matrix.
    :param z0: The port impedances (Ohms).
    :return: The chain matrix.
    """
    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    ans = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = 2 * np.sqrt(z0[0].real * z0[1].real)

    # Calculate the numerators
    ans[0,0] = z0c[0] * (t[0,0] + t[0,1]) + z0[0] * (t[1,0] + t[1,1])
    ans[0,1] = z0c[1] * (t[0,0] * z0c[0] + t[1,0] * z0[0]) - z0[1] * (t[0,1] * z0c[0] + t[1,1] * z0[0])
    ans[1,0] = t[0,0] + t[0,1] - t[1,0] - t[1,1]
    ans[1,1] = z0c[1] * (t[0,0] - t[1,0]) - z0[1] * (t[0,1] - t[1,1])

    # Return the conversion
    return ans / denominator


def abcd_to_t(abcd, z0):
    """ Chain (ABCD) to Chain Transfer (T)

    :param abcd: The chain matrix.
    :param z0: The port impedances (Ohms).
    :return: The chain transfer matrix.
    """
    # Break out the components
    A = abcd[0,0]
    B = abcd[0,1]
    C = abcd[1,0]
    D = abcd[1,1]

    # Calculate the conjugate of the port impedances
    z0c = np.matrix.conj(z0)

    # Initialize the output array
    t = np.zeros([2,2], dtype=complex)

    # Calculate the denominator
    denominator = 2 * np.sqrt(z0[0].real * z0[1].real)

    # Calculate the numerators
    t[0,0] = A * z0[1] + B + C * z0[0] * z0[1] + D * z0[0]
    t[0,1] = A * z0c[1] - B + C * z0[0] * z0c[1] - D * z0[0]
    t[1,0] = A * z0[1] + B - C * z0c[0] * z0[1] - D * z0c[0]
    t[1,1] = A * z0c[1] - B - C * z0c[0] * z0c[1] + D * z0c[0]

    # Return the conversion
    return t / denominator
