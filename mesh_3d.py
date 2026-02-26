"""mesh_3d.py — 3D mesh generation for a torospherical head.

Revolves the 2D cross-section profile around the z-axis to produce
structured surface grids suitable for matplotlib plot_surface and for
export to other 3D formats.

Coordinate system
-----------------
  X = r * cos(θ)
  Y = r * sin(θ)
  Z = z  (z=0 at open end, positive toward apex — same as 2D convention)

Public API
----------
  revolve_profile(r, z, n_az)                           → (X, Y, Z)
  build_head_mesh(D, R_c, r_k, t, h, n_mer, n_az)      → HeadMesh
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field

from geometry import build_cross_section, compute_derived_geometry, HeadGeometry


# ---------------------------------------------------------------------------
# Mesh dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HeadMesh:
    """Structured 3D surface mesh of a torospherical head.

    Grid arrays have shape (n_profile, n_az + 1):
      - Axis 0 (rows)    : meridional direction — along the profile
      - Axis 1 (columns) : azimuthal direction — angle θ around the axis

    The last column is identical to the first (θ = 2π ≡ θ = 0) to produce
    a watertight closed revolution. Similarly, the first and last profile
    rows are the same point (the profile is closed) to seal the solid.

    Fields
    ------
    X, Y, Z : np.ndarray, shape (n_profile, n_az+1)
        Cartesian coordinate grids.
    r, z_profile : np.ndarray, shape (n_profile,)
        Source 2D profile in the r-z half-plane.
    theta : np.ndarray, shape (n_az+1,)
        Azimuthal angles in radians, linspace(0, 2π, n_az+1).
    geometry : HeadGeometry
        Derived geometric quantities.
    n_meridional : int
        Arc samples per segment used when building the source profile.
    n_azimuthal : int
        Number of azimuthal subdivisions (columns = n_azimuthal + 1).
    """
    X:            np.ndarray
    Y:            np.ndarray
    Z:            np.ndarray
    r:            np.ndarray
    z_profile:    np.ndarray
    theta:        np.ndarray
    geometry:     HeadGeometry
    n_meridional: int
    n_azimuthal:  int

    # Convenience properties ------------------------------------------------

    @property
    def n_profile(self) -> int:
        """Number of points in the source profile (= X.shape[0])."""
        return self.X.shape[0]

    @property
    def n_quads(self) -> int:
        """Number of quadrilateral cells in the surface grid."""
        return (self.X.shape[0] - 1) * self.X.shape[1]

    @property
    def z_min(self) -> float:
        return float(self.Z.min())

    @property
    def z_max(self) -> float:
        return float(self.Z.max())

    @property
    def r_max(self) -> float:
        """Maximum radial extent (outer flange radius = D/2 + t)."""
        return float(np.sqrt(self.X**2 + self.Y**2).max())


# ---------------------------------------------------------------------------
# Revolution function
# ---------------------------------------------------------------------------

def revolve_profile(
    r: np.ndarray,
    z: np.ndarray,
    n_az: int = 90,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Revolve a 2D axisymmetric profile around the z-axis.

    Parameters
    ----------
    r, z : np.ndarray, shape (N,)
        Profile coordinates in the r-z half-plane. r values must be >= 0.
        The profile need not be closed; closure is handled by the azimuthal
        wrap-around (last column = first column).
    n_az : int
        Number of azimuthal subdivisions. The returned grids have n_az + 1
        columns so that theta[0] = 0 and theta[-1] = 2π are both present,
        forming a visually closed solid without any seam gaps.

    Returns
    -------
    X, Y, Z : np.ndarray, shape (N, n_az+1)
        Cartesian grids:
            X[i, j] = r[i] * cos(θ[j])
            Y[i, j] = r[i] * sin(θ[j])
            Z[i, j] = z[i]
    theta : np.ndarray, shape (n_az+1,)
        Azimuthal angles used.

    Notes
    -----
    Rows where r[i] = 0 (the centreline apex points) produce degenerate
    "pole" rows where all X[i, :] = 0 and Y[i, :] = 0. matplotlib's
    plot_surface handles these gracefully, but lighting artefacts can appear
    near the poles — managed in the visualization layer (Step 4).
    """
    if np.any(r < 0):
        raise ValueError("All r values must be >= 0 for a valid revolution.")

    theta = np.linspace(0.0, 2.0 * np.pi, n_az + 1)

    # np.outer gives shape (N, n_az+1) directly
    X = np.outer(r, np.cos(theta))
    Y = np.outer(r, np.sin(theta))
    Z = np.outer(z, np.ones(n_az + 1))

    return X, Y, Z, theta


# ---------------------------------------------------------------------------
# Top-level mesh builder
# ---------------------------------------------------------------------------

def build_head_mesh(
    D: float, R_c: float, r_k: float, t: float, h: float,
    n_meridional: int = 128,
    n_azimuthal:  int = 90,
) -> HeadMesh:
    """Build the complete 3D structured surface mesh of a torospherical head.

    Parameters
    ----------
    D, R_c, r_k, t, h : float
        Head parameters (validated inside geometry module).
    n_meridional : int
        Samples per curved arc segment when building the 2D profile.
        Total profile points ≈ 6 * n_meridional + 6 straight-segment points.
        Recommended: 64–256 depending on required smoothness.
    n_azimuthal : int
        Azimuthal subdivisions around the axis.
        Total azimuthal columns = n_azimuthal + 1.
        Recommended: 60–180 for display; 360 for near-cylindrical accuracy.

    Returns
    -------
    HeadMesh
        Structured grid with all coordinate arrays and metadata.

    Mesh density guidance
    ---------------------
    For interactive display (Step 4):   n_meridional=128, n_azimuthal=90
    For high-quality render/export:     n_meridional=256, n_azimuthal=180
    For quick validation:               n_meridional=32,  n_azimuthal=36
    """
    g = compute_derived_geometry(D, R_c, r_k, t, h)
    r_prof, z_prof = build_cross_section(D, R_c, r_k, t, h, n_arc=n_meridional)
    X, Y, Z, theta = revolve_profile(r_prof, z_prof, n_az=n_azimuthal)

    return HeadMesh(
        X=X, Y=Y, Z=Z,
        r=r_prof,
        z_profile=z_prof,
        theta=theta,
        geometry=g,
        n_meridional=n_meridional,
        n_azimuthal=n_azimuthal,
    )
