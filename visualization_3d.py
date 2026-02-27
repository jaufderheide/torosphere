"""visualization_3d.py — 3D visualization for a torospherical head.

Produces a side-by-side figure with:
  Left  — full 360° zone-coloured surface view
  Right — half-section (y ≥ 0) with a filled cross-section at the cut plane

Zone colours match the 2D validation plot (visualization_2d.py) so that
engineers and developers can cross-reference the 2D segments with the 3D surfaces.

Public API
----------
  plot_3d_head(mesh, ax, *, half_section, show_cut_face, alpha, elev, azim)
      Draws one zone-coloured 3D view into an existing (or new) Axes3D.

  plot_head_comparison(mesh, *, alpha)
      Creates a two-panel figure: full view + half-section.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from mesh_3d import HeadMesh, segment_row_ranges


# ---------------------------------------------------------------------------
# Zone colour palette  (matches visualization_2d.py for cross-reference)
# ---------------------------------------------------------------------------

SEGMENT_COLORS: dict[str, str] = {
    "Inner crown arc":        "#1565C0",   # deep blue
    "Inner knuckle arc":      "#2E7D32",   # deep green
    "Inner straight flange":  "#C62828",   # deep red
    "Bottom rim":             "#6A1B9A",   # deep purple
    "Outer straight flange":  "#E65100",   # deep orange
    "Outer knuckle arc":      "#006064",   # dark teal
    "Outer crown arc":        "#AD1457",   # deep pink
    "Apex flat":              "#37474F",   # blue-grey
}

CUT_FACE_COLOR    = "#ccdde8"   # light steel blue — the wall cross-section fill
CUT_FACE_EDGE     = "#5577aa"   # slightly darker edge line on the cut polygon


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _set_equal_aspect(ax: "Axes3D", mesh: HeadMesh) -> None:
    """Apply physically correct equal-axis scaling to a 3D axes.

    matplotlib's 3D axes do NOT enforce equal scales by default, so a
    200 mm step on the Z axis would appear the same length as a 200 mm
    step on X or Y even when the actual extents differ by 4:1.

    ``set_box_aspect`` sets the *ratio* of the rendered box dimensions
    to match the actual data extents, correcting this distortion.

    The same ranges are used for both the full and half-section views so
    that both subplots share a common visual scale.
    """
    xy = mesh.r_max * 2               # full diameter extent
    z  = mesh.z_max - mesh.z_min      # total axial height
    ax.set_box_aspect((xy, xy, z))


def _add_cut_face(ax: "Axes3D", mesh: HeadMesh) -> None:
    """Draw the wall cross-section polygon on the y = 0 cut plane.

    The filled profile polygon is drawn at both x > 0 (θ = 0) and
    x < 0 (θ = π) sides of the cut plane so the full cross-section is
    visible when the half-section is viewed from any angle.

    The polygon uses the closed profile arrays from the mesh (``mesh.r``
    and ``mesh.z_profile``), which already form a sealed loop.
    """
    r      = mesh.r
    z      = mesh.z_profile
    zeros  = np.zeros_like(r)

    for x_sign in (+1.0, -1.0):
        verts = np.column_stack([x_sign * r, zeros, z])
        poly  = Poly3DCollection(
            [verts],
            facecolor=CUT_FACE_COLOR,
            edgecolor=CUT_FACE_EDGE,
            linewidth=0.4,
            alpha=0.80,
            zorder=2,
        )
        ax.add_collection3d(poly)


# ---------------------------------------------------------------------------
# Single-panel 3D plot
# ---------------------------------------------------------------------------

def plot_3d_head(
    mesh: HeadMesh,
    ax: "Axes3D | None" = None,
    *,
    half_section: bool = False,
    show_cut_face: bool = True,
    alpha: float = 0.88,
    elev: float = 28.0,
    azim: float = -45.0,
    zone_colors: bool = True,
    single_color: str = "#4a90d9",
    stride: int = 1,
) -> "Axes3D":
    """Draw the 3D surface of a torospherical head.

    Parameters
    ----------
    mesh : HeadMesh
        Mesh produced by ``build_head_mesh``.
    ax : Axes3D or None
        Existing 3D axes to draw into.  If None, a new figure is created.
    half_section : bool
        If True, show only the y ≥ 0 half (azimuthal angles 0 → π) and
        optionally draw the cross-section cut face at y = 0.
    show_cut_face : bool
        Draw the wall cross-section fill polygon at the cut plane.
        Only has an effect when ``half_section=True``.
    alpha : float
        Opacity of the surface patches (0 = transparent, 1 = opaque).
    elev, azim : float
        Initial camera elevation and azimuth in degrees.
    zone_colors : bool
        If True (default), each of the 8 cross-section segments is drawn
        in its own colour.  If False, the entire surface uses
        ``single_color`` — faster and simpler.
    single_color : str
        Hex colour used when ``zone_colors=False``.
    stride : int
        Row/column subsampling step for ``plot_surface``.  stride=1 uses
        every mesh point (highest quality); stride=2 uses every other point
        (renders ~4× faster with minimal visible difference at screen
        resolution).  Recommended: 1 for export, 2 for interactive use.

    Returns
    -------
    ax : Axes3D

    How zone colouring works
    ------------------------
    ``segment_row_ranges(mesh.n_meridional)`` returns the row index slice
    for each of the 8 segments in the structured mesh grid.  Plotting each
    slice as a separate surface allows independent colour assignment while
    preserving the seamless join between zones (adjacent zones share a
    boundary row).
    """
    if ax is None:
        fig = plt.figure(figsize=(9, 8))
        ax  = fig.add_subplot(111, projection="3d")

    # Azimuthal column range:
    #   full view  → all columns  (θ: 0 → 2π)
    #   half view  → first half   (θ: 0 → π)
    n_half  = mesh.n_azimuthal // 2
    col_end = n_half + 1 if half_section else mesh.n_azimuthal + 1

    if zone_colors:
        # Draw each zone as its own surface patch in a distinct colour
        for name, r0, r1 in segment_row_ranges(mesh.n_meridional):
            ax.plot_surface(
                mesh.X[r0:r1 + 1, :col_end],
                mesh.Y[r0:r1 + 1, :col_end],
                mesh.Z[r0:r1 + 1, :col_end],
                color=SEGMENT_COLORS[name],
                alpha=alpha,
                linewidth=0,
                antialiased=True,
                rstride=stride, cstride=stride,
            )
    else:
        # Single-colour surface — one plot_surface call, maximum performance
        ax.plot_surface(
            mesh.X[:, :col_end],
            mesh.Y[:, :col_end],
            mesh.Z[:, :col_end],
            color=single_color,
            alpha=alpha,
            linewidth=0,
            antialiased=True,
            rstride=stride, cstride=stride,
        )

    if half_section and show_cut_face:
        _add_cut_face(ax, mesh)

    _set_equal_aspect(ax, mesh)

    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.view_init(elev=elev, azim=azim)
    return ax


# ---------------------------------------------------------------------------
# Two-panel comparison figure
# ---------------------------------------------------------------------------

def plot_head_comparison(
    mesh: HeadMesh,
    *,
    alpha: float = 0.88,
) -> plt.Figure:
    """Create a side-by-side comparison figure.

    Left panel  — full 360° zone-coloured surface
    Right panel — half-section (y ≥ 0) with wall cross-section fill

    The two views share a common colour legend at the bottom, and a
    shared title showing all five input parameters.

    Parameters
    ----------
    mesh : HeadMesh
        Mesh produced by ``build_head_mesh``.
    alpha : float
        Surface opacity.

    Returns
    -------
    fig : matplotlib Figure
    """
    fig = plt.figure(figsize=(16, 8))

    # ── Left panel: full 360° view ────────────────────────────────────────
    ax_full = fig.add_subplot(121, projection="3d")
    plot_3d_head(mesh, ax=ax_full,
                 half_section=False,
                 alpha=alpha,
                 elev=28, azim=-45)
    ax_full.set_title("Full view — zone colours", fontsize=11, pad=10)

    # ── Right panel: half-section ─────────────────────────────────────────
    ax_half = fig.add_subplot(122, projection="3d")
    plot_3d_head(mesh, ax=ax_half,
                 half_section=True,
                 show_cut_face=True,
                 alpha=alpha,
                 elev=22, azim=15)
    ax_half.set_title("Half-section (y ≥ 0) — wall thickness visible",
                      fontsize=11, pad=10)

    # ── Shared legend ─────────────────────────────────────────────────────
    legend_handles = [
        Patch(facecolor=color, label=f"{i + 1}. {name}", alpha=0.9)
        for i, (name, color) in enumerate(SEGMENT_COLORS.items())
    ] + [
        Patch(facecolor=CUT_FACE_COLOR, edgecolor=CUT_FACE_EDGE,
              label="Cut face (wall cross-section)"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=5,
        fontsize=8.5,
        framealpha=0.92,
        bbox_to_anchor=(0.5, -0.01),
    )

    # ── Shared title with all input parameters ────────────────────────────
    g = mesh.geometry
    fig.suptitle(
        "Torospherical Head\n"
        f"D = {g.D:.0f} mm    $R_c$ = {g.R_c:.0f} mm    "
        f"$r_k$ = {g.r_k:.0f} mm    t = {g.t:.0f} mm    h = {g.h:.0f} mm",
        fontsize=12,
        y=1.02,
    )

    plt.tight_layout()
    return fig
