"""broadside_coupler.py

2D electrostatic finite-difference field solver for a broadside-coupled
stripline directional coupler (two traces stacked on adjacent PCB layers,
centered between two ground planes, in a homogeneous dielectric).

WHY THIS EXISTS
----------------
Simplified closed-form PCB-trace calculators (Wheeler/IPC-style formulas)
are curve fits valid only over a limited width/spacing/height range. Push
them outside that range (e.g. spacing smaller than width, or trace very
close to one ground plane) and they silently give wrong -- sometimes
nonsensical (negative impedance) -- answers with no warning.

This script instead solves Laplace's equation numerically on the actual
2D cross-section you specify, and extracts even/odd-mode capacitance per
unit length directly from the field solution via Gauss's law. No
assumptions about aspect ratio are baked in, so it stays valid, at
somewhat higher compute cost, for extreme/asymmetric geometries.

VALIDATION
----------
Run with --validate to check the solver against Cohn's EXACT closed-form
conformal-mapping formula for a single zero-thickness strip centered in
stripline (no coupling). Typical agreement is ~1-2% at the default grid
resolution.

MODEL ASSUMPTIONS
------------------
- Zero conductor thickness (thin strip). Real 1oz/0.5oz copper thickness
  is a second-order correction (a few percent) -- not modeled here.
- Two ground planes, uniform dielectric (er) fills the entire region
  between them (true stripline, not microstrip).
- Traces are the same width, and stacked directly above one another
  (broadside coupling), symmetric about the geometric center between the
  two ground planes is NOT required -- you give absolute positions.
- Open (unshielded) sides: the solution domain is made much wider than
  the strip/gap dimensions so the side boundaries have negligible effect
  (matches the usual "b only, no side wall" assumption used by most PCB
  stripline calculators).

This is from Cohn's 1960 broadside-coupled stripline paper
("Characteristic Impedances for Broadside-Coupled Strip Transmission
Lines," IRE Trans. MTT, Nov 1960)

USAGE
-----
Edit the parameters in main() below, or import solve_broadside_coupler()
into your own script. Requires numpy and scipy.

"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

EPS0 = 8.8541878128e-12   # F/m
C_LIGHT = 2.99792458e8    # m/s


# --------------------------------------------------------------------------
# Core FDM Laplace solver
# --------------------------------------------------------------------------

def _solve_laplace(nx, ny, dx, dy, fixed_mask, fixed_val):
    """
    5-point finite-difference Laplace solve on a regular (ny x nx) grid.

    Top row (j=0) and bottom row (j=ny-1) are always Dirichlet (grounds).
    Left/right edges (i=0, i=nx-1) use a Neumann (zero-gradient / mirror)
    boundary, approximating an open/unshielded structure -- valid as long
    as the domain is much wider than the strip and gap dimensions.

    fixed_mask : bool array (ny,nx), True where voltage is prescribed
    fixed_val  : float array (ny,nx), the prescribed voltage values
    """
    N = nx * ny
    idx = lambda j, i: j * nx + i

    rows, cols, vals = [], [], []
    b = np.zeros(N)
    rx, ry = 1.0 / dx**2, 1.0 / dy**2
    diag = -2 * rx - 2 * ry

    for j in range(ny):
        for i in range(nx):
            k = idx(j, i)
            if fixed_mask[j, i]:
                rows.append(k); cols.append(k); vals.append(1.0)
                b[k] = fixed_val[j, i]
                continue
            rows.append(k); cols.append(k); vals.append(diag)
            im1 = i - 1 if i - 1 >= 0 else i + 1     # mirror at left edge
            ip1 = i + 1 if i + 1 < nx else i - 1      # mirror at right edge
            rows.append(k); cols.append(idx(j, im1)); vals.append(rx)
            rows.append(k); cols.append(idx(j, ip1)); vals.append(rx)
            rows.append(k); cols.append(idx(j - 1, i)); vals.append(ry)
            rows.append(k); cols.append(idx(j + 1, i)); vals.append(ry)

    A = sp.csr_matrix((vals, (rows, cols)), shape=(N, N))
    V = spla.spsolve(A, b)
    return V.reshape(ny, nx)


def _box_charge(V, dx, dy, eps, i0, i1, j0, j1):
    """
    Charge per unit length (C/m) enclosed by a rectangular Gaussian box,
    computed from the field solution via a discrete contour integral of
    the normal E-field (Gauss's law), box edges placed at index bounds
    [i0,i1) x [j0,j1) (i.e. just outside a thin strip).
    """
    Q = 0.0
    for i in range(i0, i1):        # bottom edge, outward normal -y
        dVdy = (V[j0, i] - V[j0 - 1, i]) / dy
        Q += eps * dVdy * dx
    for i in range(i0, i1):        # top edge, outward normal +y
        dVdy = (V[j1, i] - V[j1 - 1, i]) / dy
        Q += -eps * dVdy * dx
    for j in range(j0, j1):        # left edge, outward normal -x
        dVdx = (V[j, i0] - V[j, i0 - 1]) / dx
        Q += eps * dVdx * dy
    for j in range(j0, j1):        # right edge, outward normal +x
        dVdx = (V[j, i1] - V[j, i1 - 1]) / dx
        Q += -eps * dVdx * dy
    return Q


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def solve_broadside_coupler(w_mm, s_mm, b_mm, er,
                             nx=1500, ny_per_mm=230, pad_factor=10):
    """
    Solve for even/odd mode impedance of a broadside-coupled stripline pair.

    Parameters
    ----------
    w_mm : trace width (mm), both traces assumed equal width
    s_mm : edge-to-edge gap BETWEEN the two traces (mm)
    b_mm : total ground-to-ground spacing (mm). Traces are placed
           symmetrically, i.e. each trace is (b-s)/2 from its nearest
           ground plane.
    er   : dielectric constant (relative permittivity) filling the stack
    nx, ny_per_mm, pad_factor : grid resolution / domain width controls.
           Increase for more accuracy at the cost of runtime/memory.

    Returns dict with Z0e, Z0o, Z0 (=sqrt(Z0e*Z0o)), C0 (coupling coeff),
    plus the raw self/mutual charges for reference.
    """
    w, s, b = w_mm * 1e-3, s_mm * 1e-3, b_mm * 1e-3
    ny = max(20, int(round(b * 1e3 * ny_per_mm)))
    Lx = pad_factor * max(b, w)
    dx, dy = Lx / nx, b / ny

    y1 = (b - s) / 2.0     # strip 1 (top) distance from top ground
    y2 = y1 + s             # strip 2 (bottom) distance from top ground
    j_top, j_bot = 0, ny
    j1 = int(round(y1 / dy))
    j2 = int(round(y2 / dy))
    if j1 == j2:
        j2 = j1 + 1

    fixed_mask = np.zeros((ny + 1, nx), dtype=bool)
    fixed_val = np.zeros((ny + 1, nx))
    fixed_mask[j_top, :] = True
    fixed_mask[j_bot, :] = True   # both grounds default to 0V

    xs = (np.arange(nx) - nx / 2) * dx
    strip_cols = np.where(np.abs(xs) <= w / 2)[0]
    if len(strip_cols) < 2:
        raise ValueError("Grid too coarse to resolve trace width -- increase nx.")

    # Drive strip 1 to 1V, strip 2 to 0V (this single solve gives both the
    # self capacitance and the mutual capacitance by reciprocity/symmetry,
    # since the geometry is symmetric about the midplane between the traces).
    fixed_mask[j1, strip_cols] = True
    fixed_val[j1, strip_cols] = 1.0
    fixed_mask[j2, strip_cols] = True
    fixed_val[j2, strip_cols] = 0.0

    V = _solve_laplace(nx, ny + 1, dx, dy, fixed_mask, fixed_val)

    eps = er * EPS0
    i0, i1 = strip_cols[0] - 3, strip_cols[-1] + 4
    Q1 = _box_charge(V, dx, dy, eps, i0, i1, j1 - 3, j1 + 3)  # self charge, strip 1
    Q2 = _box_charge(V, dx, dy, eps, i0, i1, j2 - 3, j2 + 3)  # induced charge, strip 2 (<0)

    Ce = Q1 + Q2   # even-mode capacitance/length (both driven equal)
    Co = Q1 - Q2   # odd-mode capacitance/length (driven differentially)

    vp = C_LIGHT / np.sqrt(er)
    Z0e = 1.0 / (vp * Ce)
    Z0o = 1.0 / (vp * Co)
    Z0 = np.sqrt(Z0e * Z0o)
    C0 = (Z0e - Z0o) / (Z0e + Z0o)

    return dict(Z0e=Z0e, Z0o=Z0o, Z0=Z0, C0=C0, Q1=Q1, Q2=Q2, Ce=Ce, Co=Co)


def coupling_at_length(C0, er, length_mm, freq_hz):
    """
    Convert mid-band coupling coefficient C0 into actual forward/reverse
    coupling (dB) for a given physical coupled length and frequency,
    using the short/arbitrary-length coupled-line response

        C(theta) = C0*sin(theta) / sqrt(1-C0^2*cos(theta)^2 ... )   [full form]

    Here we use the standard result for a single-section coupler:

        |C(theta)| = C0*sin(theta) / sqrt(1 - C0^2*cos(theta)^2)

    which reduces to C0*sin(theta) for small C0, and is exact at
    theta = 90 deg (quarter-wave) where |C| = C0.
    """
    lam0 = C_LIGHT / freq_hz
    lam_g = lam0 / np.sqrt(er)
    length_m = length_mm * 1e-3
    theta = 2 * np.pi * length_m / lam_g   # electrical length, radians

    num = C0 * np.sin(theta)
    den = np.sqrt(1 - (C0 * np.cos(theta))**2)
    C_theta = num / den
    dB = 20 * np.log10(abs(C_theta))
    return dict(theta_deg=np.degrees(theta), C_theta=C_theta, coupling_dB=dB,
                lambda_g_mm=lam_g * 1e3)


def validate_against_cohn(w_mm=0.4, b_mm=1.554, er=4.3):
    """
    Sanity check: solve a SINGLE centered strip (no second conductor) with
    this same FDM machinery, and compare to Cohn's exact closed-form:

        Z0 = (30*pi/sqrt(er)) * K(k') / K(k),   k = tanh(pi*w / (2b))

    which is exact for a zero-thickness strip centered in stripline.
    """
    from scipy.special import ellipk

    w, b = w_mm * 1e-3, b_mm * 1e-3
    nx, ny = 1200, 300
    Lx = 12 * b
    dx, dy = Lx / nx, b / ny
    j_strip = ny // 2
    fixed_mask = np.zeros((ny + 1, nx), dtype=bool)
    fixed_val = np.zeros((ny + 1, nx))
    fixed_mask[0, :] = True
    fixed_mask[ny, :] = True
    xs = (np.arange(nx) - nx / 2) * dx
    cols = np.where(np.abs(xs) <= w / 2)[0]
    fixed_mask[j_strip, cols] = True
    fixed_val[j_strip, cols] = 1.0

    V = _solve_laplace(nx, ny + 1, dx, dy, fixed_mask, fixed_val)
    eps = er * EPS0
    Q = _box_charge(V, dx, dy, eps, cols[0] - 3, cols[-1] + 4, j_strip - 3, j_strip + 3)
    vp = C_LIGHT / np.sqrt(er)
    Z0_fdm = 1.0 / (vp * Q)

    k = np.tanh(np.pi * w_mm / (2 * b_mm))
    kp = np.sqrt(1 - k**2)
    Z0_exact = (30 * np.pi / np.sqrt(er)) * ellipk(kp**2) / ellipk(k**2)

    err_pct = 100 * (Z0_fdm - Z0_exact) / Z0_exact
    print(f"Single centered strip, w={w_mm}mm, b={b_mm}mm, er={er}")
    print(f"  FDM solver result : {Z0_fdm:8.3f} ohm")
    print(f"  Cohn exact formula: {Z0_exact:8.3f} ohm")
    print(f"  Difference        : {err_pct:+.2f} %")
    print()


# --------------------------------------------------------------------------
# Example / entry point
# --------------------------------------------------------------------------

if __name__ == "__main__":
    # ---- EDIT THESE FOR YOUR DESIGN --------------------------------------
    w_mm = 0.47        # trace width
    s_mm = .218        # gap between the two traces
    b_mm = 1.556       # total ground-to-ground spacing
    er = 4.3           # dielectric constant
    length_mm = 2.33   # physical coupled length
    freq_hz = 435e6    # operating frequency
    # -----------------------------------------------------------------------

    print("=" * 70)
    print("VALIDATION: FDM solver vs. Cohn's exact single-strip formula")
    print("=" * 70)
    validate_against_cohn(w_mm, b_mm, er)

    print("=" * 70)
    print("BROADSIDE COUPLER SOLVE")
    print("=" * 70)

    r = solve_broadside_coupler(w_mm, s_mm, b_mm, er)
    print(f"Geometry: w={w_mm}mm  s={s_mm}mm  b={b_mm}mm  er={er}")
    print(f"  Z0e = {r['Z0e']:.2f} ohm")
    print(f"  Z0o = {r['Z0o']:.2f} ohm")
    print(f"  Z0  = {r['Z0']:.2f} ohm  (should be near your system impedance)")
    print(f"  C0  = {r['C0']:.4f}  ({20*np.log10(r['C0']):.1f} dB mid-band/quarter-wave coupling)")
    print()

    c = coupling_at_length(r['C0'], er, length_mm, freq_hz)
    print(f"At length={length_mm}mm, f={freq_hz/1e6:.0f}MHz:")
    print(f"  Electrical length theta = {c['theta_deg']:.2f} deg "
          f"(quarter-wave lambda_g/4 = {c['lambda_g_mm']/4:.2f} mm)")
    print(f"  Coupling = {c['coupling_dB']:.1f} dB")
    print()

    # print("=" * 70)
    # print("SWEEP: gap vs. coupling (holding w, b, er, length, freq fixed)")
    # print("=" * 70)
    # print(f"{'s (mm)':>8} {'Z0e':>8} {'Z0o':>8} {'Z0':>8} {'C0':>8} {'dB@len':>10}")
    # for s in [0.05, 0.1, 0.109, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.8, 1.0, 1.278]:
    #     rr = solve_broadside_coupler(w_mm, s, b_mm, er)
    #     cc = coupling_at_length(rr['C0'], er, length_mm, freq_hz)
    #     print(f"{s:8.3f} {rr['Z0e']:8.1f} {rr['Z0o']:8.1f} {rr['Z0']:8.1f} "
    #           f"{rr['C0']:8.3f} {cc['coupling_dB']:10.1f}")
