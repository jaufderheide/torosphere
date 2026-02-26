"""visualization_2d.py — 2D cross-section validation plot for a torospherical head.

Public API
----------
  plot_cross_section_validation(D, R_c, r_k, t, h, n_arc)
      Draws a fully annotated validation figure. Shows colour-coded profile
      segments, construction ghost arcs, tangency markers, knuckle centre
      markers, dimension annotations, and a derived-geometry summary.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from geometry import build_cross_section_segments, compute_derived_geometry

# ---------------------------------------------------------------------------
# Segment colour palette
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


# ---------------------------------------------------------------------------
# Private drawing helpers
# ---------------------------------------------------------------------------

def _dim_arrow(
    ax: plt.Axes,
    x1: float, y1: float, x2: float, y2: float,
    label: str,
    lx: float | None = None, ly: float | None = None,
    color: str = "#555555", fs: float = 8.0,
) -> None:
    """Draw a double-headed dimension arrow with a centred label."""
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="<->", color=color, lw=1.0,
                        mutation_scale=10),
        zorder=7,
    )
    lx = (x1 + x2) / 2 if lx is None else lx
    ly = (y1 + y2) / 2 if ly is None else ly
    ax.text(lx, ly, label, ha="center", va="center", fontsize=fs,
            color=color, bbox=dict(fc="white", ec="none", pad=1.5), zorder=8)


def _ext_line(ax: plt.Axes,
              x1: float, y1: float, x2: float, y2: float) -> None:
    """Draw a thin dotted extension line (for dimension witness lines)."""
    ax.plot([x1, x2], [y1, y2], color="#aaaaaa", lw=0.6, ls=":", zorder=1)


# ---------------------------------------------------------------------------
# Main validation plot
# ---------------------------------------------------------------------------

def plot_cross_section_validation(
    D: float, R_c: float, r_k: float, t: float, h: float,
    n_arc: int = 128,
) -> None:
    """Draw the 2D cross-section validation figure.

    Parameters
    ----------
    D, R_c, r_k, t, h : float
        Head parameters.
    n_arc : int
        Samples per arc segment (higher = smoother curves).

    What to inspect
    ---------------
    1. Profile joins — no visible kinks at segment junctions (confirms G1
       tangency at crown–knuckle joints).
    2. Tangency markers (gold circles) — must sit exactly on the profile line.
    3. Ghost arcs — colour-matched dashed extensions of crown sphere and
       knuckle torus; profile arcs should lie cleanly on them.
    4. Dimension annotations — should match the input parameters exactly.
    5. Derived geometry panel — cross-check key values (z_sc, alpha, dome
       height) against hand calculations.
    """
    g = compute_derived_geometry(D, R_c, r_k, t, h)
    segments, _ = build_cross_section_segments(D, R_c, r_k, t, h, n_arc)

    r_kc = D / 2 - r_k   # knuckle centre, radial
    z_kc = h              # knuckle centre, axial

    # --- Layout geometry ------------------------------------------------
    x_margin = max(t * 22, D * 0.22)
    z_lo     = -(h + t * 9)          # room for dimension lines below flange
    z_hi     = g.z_apex_outer + t * 5

    fig, ax = plt.subplots(figsize=(10, 11))

    # ── Filled cross-section (both sides) ────────────────────────────────
    r_all = np.concatenate([s[1] for s in segments])
    z_all = np.concatenate([s[2] for s in segments])
    ax.fill( r_all, z_all, color="#d6e4f5", alpha=0.55, zorder=1)
    ax.fill(-r_all, z_all, color="#d6e4f5", alpha=0.55, zorder=1)

    # ── Left mirror (grey, faded for visual context) ──────────────────────
    for _, r, z in segments:
        ax.plot(-r, z, color="#999999", lw=1.2, alpha=0.35, zorder=2)

    # ── Right side: colour-coded named segments ───────────────────────────
    for name, r, z in segments:
        ax.plot(r, z, color=SEGMENT_COLORS[name], lw=2.5, zorder=4,
                solid_capstyle="round")

    # ── Construction ghost arcs (dashed, same colour as segment, faded) ──
    phi_ext   = np.linspace(0.0, g.phi_t * 1.12, 80)
    theta_ext = np.linspace(-0.08, g.alpha + 0.12, 80)

    for radius, col in [
        (g.R_c,       SEGMENT_COLORS["Inner crown arc"]),
        (g.R_c + t,   SEGMENT_COLORS["Outer crown arc"]),
    ]:
        rg = radius * np.sin(phi_ext)
        zg = g.z_sc + radius * np.cos(phi_ext)
        ax.plot(rg, zg, ls="--", color=col, lw=0.9, alpha=0.35, zorder=2)

    for radius, col in [
        (r_k,       SEGMENT_COLORS["Inner knuckle arc"]),
        (r_k + t,   SEGMENT_COLORS["Outer knuckle arc"]),
    ]:
        rg = r_kc + radius * np.cos(theta_ext)
        zg = z_kc + radius * np.sin(theta_ext)
        ax.plot(rg, zg, ls="--", color=col, lw=0.9, alpha=0.35, zorder=2)

    # ── Tangency point markers ─────────────────────────────────────────────
    for sign in (+1, -1):
        ax.plot([sign * g.r_t,     sign * g.r_t_out],
                [g.z_t,            g.z_t_out],
                "o", ms=7, color="gold", mec="#333333", mew=0.9, zorder=6)

    # ── Knuckle centre markers + r_k radius arrow ─────────────────────────
    for sign in (+1, -1):
        ax.plot(sign * r_kc, z_kc, "k^", ms=7, zorder=5)

    ax.annotate(
        "", xy=(g.r_t, g.z_t), xytext=(r_kc, z_kc),
        arrowprops=dict(arrowstyle="-|>",
                        color=SEGMENT_COLORS["Inner knuckle arc"],
                        lw=1.0, mutation_scale=9),
        zorder=5,
    )
    mr = (r_kc + g.r_t) / 2
    mz = (z_kc + g.z_t) / 2
    ax.text(mr + t * 1.5, mz + t * 0.6,
            f"$r_k$={r_k:.0f}",
            fontsize=8.5, color=SEGMENT_COLORS["Inner knuckle arc"],
            va="center",
            bbox=dict(fc="white", ec="none", pad=1))

    # ── R_c annotation — arrow to mid-point of inner crown arc ────────────
    phi_mid  = g.phi_t / 2
    r_arc_mid = g.R_c * np.sin(phi_mid)
    z_arc_mid = g.z_sc + g.R_c * np.cos(phi_mid)
    ax.annotate(
        f"$R_c$={R_c:.0f}",
        xy=(r_arc_mid, z_arc_mid),
        xytext=(r_arc_mid + t * 7, z_arc_mid - t * 2.5),
        fontsize=8.5, color=SEGMENT_COLORS["Inner crown arc"],
        arrowprops=dict(arrowstyle="-|>",
                        color=SEGMENT_COLORS["Inner crown arc"],
                        lw=0.9, mutation_scale=8),
        bbox=dict(fc="white", ec="none", pad=1),
        zorder=7,
    )

    # ── Centreline ────────────────────────────────────────────────────────
    ax.axvline(0, color="#cccccc", lw=0.8, ls="--", zorder=0)

    # ── Dimension annotations ─────────────────────────────────────────────
    r_outer = D / 2 + t

    # h — flange height (right side)
    x_h = r_outer + t * 7
    _ext_line(ax, r_outer, 0,   x_h + t, 0)
    _ext_line(ax, r_outer, h,   x_h + t, h)
    _dim_arrow(ax, x_h, 0, x_h, h,
               f"h={h:.0f}",
               lx=x_h + t * 3.5, ly=h / 2)

    # t — shell thickness (horizontal at z = h/2)
    _dim_arrow(ax, D / 2, h / 2, r_outer, h / 2,
               f"t={t:.0f}",
               ly=h / 2 + t * 2.2)

    # D/2 — inside radius (below profile)
    z_D = -(h + t * 5)
    _ext_line(ax, 0,      0,  0,      z_D - t * 0.5)
    _ext_line(ax, D / 2,  0,  D / 2,  z_D - t * 0.5)
    _dim_arrow(ax, 0, z_D, D / 2, z_D,
               f"D/2={D/2:.0f}",
               ly=z_D - t * 2.8)

    # ── Derived geometry summary (text box) ───────────────────────────────
    osc_note = f"  (off-screen, plot clips at z={z_lo:.0f})" if g.z_sc < z_lo else ""
    summary = (
        f"Derived geometry\n"
        f"  $z_{{sc}}$ = {g.z_sc:.1f} mm{osc_note}\n"
        f"  $\\alpha$ = {np.degrees(g.alpha):.2f}°  "
        f"  $\\phi_t$ = {np.degrees(g.phi_t):.2f}°\n"
        f"  Inner tangency: r={g.r_t:.1f}, z={g.z_t:.1f} mm\n"
        f"  Outer tangency: r={g.r_t_out:.1f}, z={g.z_t_out:.1f} mm\n"
        f"  Dome height above flange: {g.z_apex_inner - h:.1f} mm"
    )
    ax.text(
        0.02, 1.7, summary,
        transform=ax.transAxes,
        va="top", ha="left", fontsize=7.5,
        family="monospace",
        bbox=dict(fc="white", ec="#cccccc", pad=6, alpha=0.92),
        zorder=9,
    )

    # ── Legend ─────────────────────────────────────────────────────────────
    legend_handles = [
        Line2D([0], [0], color=c, lw=2.5, label=f"{i+1}. {n}")
        for i, (n, c) in enumerate(SEGMENT_COLORS.items())
    ] + [
        Line2D([0], [0], marker="o", ls="", color="gold",
               mec="#333333", ms=7,
               label="Crown–knuckle tangency point"),
        Line2D([0], [0], marker="^", ls="", color="k",
               ms=7, label="Knuckle centre $O_{kc}$"),
        Line2D([0], [0], ls="--", color="#888888", lw=1.0,
               label="Construction ghost arc"),
    ]
    ax.legend(handles=legend_handles,bbox_to_anchor=(1.05, 0), loc='lower left', fontsize=7.5, framealpha=0.92, ncol=1)

    # ── Axes & title ──────────────────────────────────────────────────────
    ax.set_aspect("equal")
    ax.set_xlim(-(D / 2 + t + x_margin), D / 2 + t + x_margin)
    ax.set_ylim(z_lo, z_hi)
    ax.set_xlabel("r  (mm)")
    ax.set_ylabel("z  (mm)")
    ax.set_title(
        "Torospherical Head — Cross-Section Validation\n"
        f"D={D:.0f}  $R_c$={R_c:.0f}  $r_k$={r_k:.0f}  "
        f"t={t:.0f}  h={h:.0f}  (mm)"
    )
    ax.grid(True, alpha=0.18)
    plt.tight_layout()
    plt.show()
