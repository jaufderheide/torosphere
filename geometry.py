"""geometry.py — Torospherical head cross-section geometry.

Coordinate convention
---------------------
  r : radial distance from the centreline axis  (r >= 0)
  z : axial distance, z = 0 at the open (flange) end, positive toward apex

All input dimensions must use consistent units (e.g. mm throughout).

Public API
----------
  validate_inputs(D, R_c, r_k, t, h)          → raises ValueError on bad inputs
  compute_derived_geometry(D, R_c, r_k, t, h)  → HeadGeometry dataclass
  build_cross_section(D, R_c, r_k, t, h, ...)  → (r, z) closed profile arrays
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Dataclass for derived geometric quantities
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HeadGeometry:
    """All derived geometric quantities for a torospherical head."""

    # --- inputs ---
    D: float    # inside diameter
    R_c: float  # crown radius (inner surface)
    r_k: float  # knuckle radius (inner surface)
    t: float    # shell thickness
    h: float    # straight flange height

    # --- derived ---
    z_sc: float   # crown sphere centre z-coordinate (may be negative)
    alpha: float  # knuckle arc sweep angle, rad  (from horizontal to tangency)
    phi_t: float  # crown arc polar angle to tangency point, rad (from apex)

    r_t: float      # inner tangency point, radial
    z_t: float      # inner tangency point, axial

    r_t_out: float  # outer tangency point, radial
    z_t_out: float  # outer tangency point, axial

    z_apex_inner: float  # z at inner apex (r = 0)
    z_apex_outer: float  # z at outer apex (r = 0)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def validate_inputs(D: float, R_c: float, r_k: float, t: float, h: float) -> None:
    """Validate torospherical head parameters.

    Raises
    ------
    ValueError
        If any parameter is outside its valid range or violates a geometric
        constraint that would produce imaginary or degenerate geometry.
    """
    if D <= 0:
        raise ValueError(f"Inside diameter D must be positive (got D={D})")
    if t <= 0:
        raise ValueError(f"Shell thickness t must be positive (got t={t})")
    if r_k <= 0:
        raise ValueError(f"Knuckle radius r_k must be positive (got r_k={r_k})")
    if h < 0:
        raise ValueError(f"Straight flange height h must be non-negative (got h={h})")
    if R_c < D / 2:
        raise ValueError(
            f"Crown radius R_c ({R_c}) must be >= D/2 ({D / 2:.4g})"
        )
    if r_k >= D / 2:
        raise ValueError(
            f"Knuckle radius r_k ({r_k}) must be < D/2 ({D / 2:.4g})"
        )
    if t >= r_k:
        raise ValueError(
            f"Shell thickness t ({t}) must be < knuckle radius r_k ({r_k}) "
            "(outer knuckle would self-intersect)"
        )
    ratio = (D / 2 - r_k) / (R_c - r_k)
    if ratio >= 1.0:
        raise ValueError(
            f"Geometric constraint violated: (D/2 - r_k) / (R_c - r_k) = {ratio:.6f} >= 1.0. "
            "Crown sphere cannot span the knuckle — increase R_c or decrease r_k."
        )


# ---------------------------------------------------------------------------
# Derived geometry
# ---------------------------------------------------------------------------

def compute_derived_geometry(
    D: float, R_c: float, r_k: float, t: float, h: float
) -> HeadGeometry:
    """Compute all derived geometric quantities for a torospherical head.

    Parameters
    ----------
    D    : inside diameter
    R_c  : crown radius (inner surface)
    r_k  : knuckle radius (inner surface)
    t    : shell thickness
    h    : straight flange height

    Returns
    -------
    HeadGeometry
        Frozen dataclass containing all derived quantities.

    Notes
    -----
    z_sc is frequently negative for typical proportions (e.g. R_c = D).
    Only a shallow spherical cap — not the full hemisphere — forms the dome.

    The outer arcs (radius R_c+t and r_k+t) share the same centre points as
    the inner arcs, so alpha and phi_t are identical for inner and outer.
    This follows from the uniform normal-offset (parallel curve) property.
    """
    validate_inputs(D, R_c, r_k, t, h)

    # Sphere centre z-coordinate.
    # Derived from tangency condition: distance(O_sphere, O_knuckle) = R_c - r_k
    z_sc = h - np.sqrt((R_c - r_k) ** 2 - (D / 2 - r_k) ** 2)

    # Shared angular ratio (same for inner and outer surfaces)
    ratio = (D / 2 - r_k) / (R_c - r_k)
    alpha = np.arccos(ratio)   # knuckle arc angle from horizontal to tangency
    phi_t = np.arcsin(ratio)   # crown arc polar angle from apex to tangency
    # Note: alpha + phi_t = pi/2 (complementary angles, geometrically required)

    # Inner tangency point
    r_t = R_c * (D / 2 - r_k) / (R_c - r_k)
    z_t = z_sc + np.sqrt(R_c ** 2 - r_t ** 2)

    # Outer tangency point
    r_t_out = (R_c + t) * (D / 2 - r_k) / (R_c - r_k)
    z_t_out = z_sc + np.sqrt((R_c + t) ** 2 - r_t_out ** 2)

    # Apex heights (on centreline axis, r = 0)
    z_apex_inner = z_sc + R_c
    z_apex_outer = z_sc + R_c + t

    return HeadGeometry(
        D=D, R_c=R_c, r_k=r_k, t=t, h=h,
        z_sc=z_sc,
        alpha=alpha, phi_t=phi_t,
        r_t=r_t, z_t=z_t,
        r_t_out=r_t_out, z_t_out=z_t_out,
        z_apex_inner=z_apex_inner,
        z_apex_outer=z_apex_outer,
    )


# ---------------------------------------------------------------------------
# Private segment samplers
# ---------------------------------------------------------------------------

def _arc_crown(
    R: float, z_sc: float, phi_start: float, phi_end: float, n: int
) -> tuple[np.ndarray, np.ndarray]:
    """Sample n points on a crown (spherical) arc.

    phi is the polar angle from the +z axis (apex = 0).
    """
    phi = np.linspace(phi_start, phi_end, n)
    return R * np.sin(phi), z_sc + R * np.cos(phi)


def _arc_knuckle(
    r_kc: float, z_kc: float, r_k: float,
    theta_start: float, theta_end: float, n: int
) -> tuple[np.ndarray, np.ndarray]:
    """Sample n points on a knuckle (toroidal) arc.

    theta is measured from the positive-r axis at the knuckle centre.
    theta = 0  → junction with straight flange (r = r_kc + r_k)
    theta = alpha → tangency point with crown arc
    """
    theta = np.linspace(theta_start, theta_end, n)
    return r_kc + r_k * np.cos(theta), z_kc + r_k * np.sin(theta)


# ---------------------------------------------------------------------------
# Cross-section profile builder
# ---------------------------------------------------------------------------

def build_cross_section(
    D: float, R_c: float, r_k: float, t: float, h: float,
    n_arc: int = 64,
) -> tuple[np.ndarray, np.ndarray]:
    """Build the closed 2D cross-section profile of a torospherical head.

    The profile is a closed polygon in the (r, z) half-plane (r >= 0).
    It is traversed counter-clockwise: inner surface first (apex → flange),
    then outer surface back (flange → apex), then closed at the axis.

    Parameters
    ----------
    D, R_c, r_k, t, h : float
        Head parameters (see validate_inputs for constraints).
    n_arc : int
        Number of sample points per curved arc segment.
        Straight segments always use 2 points.

    Returns
    -------
    r, z : np.ndarray
        Arrays of shape (N,) giving the closed profile.
        First and last points are identical (r[0]==r[-1], z[0]==z[-1]).

    Segment map
    -----------
    1. Inner crown arc   : phi  0      → phi_t   (apex to knuckle tangency)
    2. Inner knuckle arc : theta alpha → 0       (tangency to flange junction)
    3. Inner straight flange : z  h → 0
    4. Bottom rim            : r  D/2 → D/2+t
    5. Outer straight flange : z  0 → h
    6. Outer knuckle arc : theta 0 → alpha
    7. Outer crown arc   : phi  phi_t → 0        (knuckle tangency to apex)
    8. Apex flat         : r = 0, z  z_apex_outer → z_apex_inner (closes loop)
    """
    g = compute_derived_geometry(D, R_c, r_k, t, h)

    r_kc = D / 2 - r_k  # knuckle arc centre, radial
    z_kc = h             # knuckle arc centre, axial

    rs, zs = [], []  # will collect (r-array, z-array) per segment

    def append(r_arr, z_arr, last: bool = False) -> None:
        """Add segment, dropping the last point unless it is the final one."""
        rs.append(r_arr if last else r_arr[:-1])
        zs.append(z_arr if last else z_arr[:-1])

    # 1. Inner crown arc: phi 0 → phi_t
    sr, sz = _arc_crown(g.R_c, g.z_sc, 0.0, g.phi_t, n_arc)
    append(sr, sz)

    # 2. Inner knuckle arc: theta alpha → 0
    sr, sz = _arc_knuckle(r_kc, z_kc, r_k, g.alpha, 0.0, n_arc)
    append(sr, sz)

    # 3. Inner straight flange: z h → 0
    append(np.array([D / 2, D / 2]), np.array([h, 0.0]))

    # 4. Bottom rim: r D/2 → D/2+t
    append(np.array([D / 2, D / 2 + t]), np.array([0.0, 0.0]))

    # 5. Outer straight flange: z 0 → h
    append(np.array([D / 2 + t, D / 2 + t]), np.array([0.0, h]))

    # 6. Outer knuckle arc: theta 0 → alpha
    sr, sz = _arc_knuckle(r_kc, z_kc, r_k + t, 0.0, g.alpha, n_arc)
    append(sr, sz)

    # 7. Outer crown arc: phi phi_t → 0
    sr, sz = _arc_crown(g.R_c + t, g.z_sc, g.phi_t, 0.0, n_arc)
    append(sr, sz)

    # 8. Apex flat: r=0, z_apex_outer → z_apex_inner  (closes the loop)
    append(np.array([0.0, 0.0]), np.array([g.z_apex_outer, g.z_apex_inner]),
           last=True)

    r = np.concatenate(rs)
    z = np.concatenate(zs)

    # Explicitly close the loop
    r = np.append(r, r[0])
    z = np.append(z, z[0])

    return r, z


def build_cross_section_segments(
    D: float, R_c: float, r_k: float, t: float, h: float,
    n_arc: int = 64,
) -> tuple[list[tuple[str, np.ndarray, np.ndarray]], HeadGeometry]:
    """Build the cross-section as individually named segments.

    Unlike build_cross_section, segments are NOT de-duplicated at junctions
    — each is returned as a complete independent array including both endpoints.
    This is required for colour-coded visualisation where segment identity
    must be preserved.

    Parameters
    ----------
    D, R_c, r_k, t, h : float
        Head parameters (see validate_inputs for constraints).
    n_arc : int
        Number of sample points per curved arc segment.

    Returns
    -------
    segments : list of (name, r, z) tuples
        Named arrays for each of the 8 profile segments, in traversal order.
    g : HeadGeometry
        Derived geometry for this head.
    """
    g = compute_derived_geometry(D, R_c, r_k, t, h)
    r_kc = D / 2 - r_k
    z_kc = h

    segs: list[tuple[str, np.ndarray, np.ndarray]] = []

    r, z = _arc_crown(g.R_c, g.z_sc, 0.0, g.phi_t, n_arc)
    segs.append(("Inner crown arc", r, z))

    r, z = _arc_knuckle(r_kc, z_kc, r_k, g.alpha, 0.0, n_arc)
    segs.append(("Inner knuckle arc", r, z))

    segs.append(("Inner straight flange",
                 np.array([D / 2, D / 2]), np.array([h, 0.0])))

    segs.append(("Bottom rim",
                 np.array([D / 2, D / 2 + t]), np.array([0.0, 0.0])))

    segs.append(("Outer straight flange",
                 np.array([D / 2 + t, D / 2 + t]), np.array([0.0, h])))

    r, z = _arc_knuckle(r_kc, z_kc, r_k + t, 0.0, g.alpha, n_arc)
    segs.append(("Outer knuckle arc", r, z))

    r, z = _arc_crown(g.R_c + t, g.z_sc, g.phi_t, 0.0, n_arc)
    segs.append(("Outer crown arc", r, z))

    segs.append(("Apex flat",
                 np.array([0.0, 0.0]),
                 np.array([g.z_apex_outer, g.z_apex_inner])))

    return segs, g
