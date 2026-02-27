"""gui.py — Simple launcher GUI for the torospherical head visualizer.

How it works
------------
A small matplotlib window displays four buttons, one for each view.
Clicking a button:
  1. Closes the launcher window.
  2. Opens the selected plot in a full-size window.
  3. When that plot window is closed, the launcher reopens automatically.

This "modal loop" means only one plot is ever rendered at a time, which
solves the performance problem of rendering multiple 3D surfaces at once.

The 3D mesh is built once at startup and reused for all 3D views.
Mesh resolution is set to a moderate value (n_meridional=64, n_azimuthal=60)
for interactive use.  Increase N_MER / N_AZ at the top of this file for
higher quality renders (at the cost of slower response).

Usage
-----
    python main.py          ← launches the GUI
    python gui.py           ← also works directly

Views available
---------------
  1. 2D Cross-Section Validation
       Annotated 2D r-z profile with segment colours, ghost arcs,
       tangency markers, and dimension annotations.

  2. 3D Simple (single colour)
       Plain blue solid — fastest render.  Good for checking overall shape
       and the equal-aspect scaling.

  3. 3D Zone-Coloured
       Each of the 8 geometric zones shown in a distinct colour matching
       the 2D validation plot.

  4. 3D Half-Section + Cutaway
       Zone-coloured, clipped at y = 0 to show the wall cross-section.
       Reveals shell thickness and the inner profile.
"""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.widgets import Button

from mesh_3d import build_head_mesh
from visualization_2d import plot_cross_section_validation
from visualization_3d import plot_3d_head, SEGMENT_COLORS, CUT_FACE_COLOR, CUT_FACE_EDGE

# ---------------------------------------------------------------------------
# Head parameters — edit these to change the geometry
# ---------------------------------------------------------------------------
D   = 1524.0   # inside diameter          (mm)
R_c = 1524.0   # crown radius, inner      (mm)
r_k =  100.0   # knuckle radius, inner    (mm)
t   =   10.0   # shell thickness          (mm)
h   =   50.0   # straight flange height   (mm)

# ---------------------------------------------------------------------------
# Mesh resolution for interactive use
# Increase for higher quality; decrease for faster response.
# ---------------------------------------------------------------------------
N_MER  = 64    # arc samples per curved segment   (profile resolution)
N_AZ   = 60    # azimuthal divisions              (roundness)
STRIDE = 2     # render every Nth mesh row/col    (1 = full, 2 = 4× faster)


# ---------------------------------------------------------------------------
# Button definitions
# (label, view_key)  — view_key is passed to _open_view()
# ---------------------------------------------------------------------------
_BUTTONS = [
    ("1 — 2D Cross-Section Validation",      "2d"),
    ("2 — 3D Simple (single colour)",        "simple"),
    ("3 — 3D Zone-Coloured",                 "zones"),
    ("4 — 3D Half-Section + Cutaway",        "half"),
]

# Colours for the launcher buttons (normal, hover)
_BTN_COLOR       = "#e8f0fe"
_BTN_HOVER_COLOR = "#b8d0f0"


# ---------------------------------------------------------------------------
# Mesh cache  (built once, reused for all 3D views)
# ---------------------------------------------------------------------------
_mesh = None


def _get_mesh():
    """Build (or return the cached) 3D mesh."""
    global _mesh
    if _mesh is None:
        print("Building mesh … ", end="", flush=True)
        _mesh = build_head_mesh(
            D, R_c, r_k, t, h,
            n_meridional=N_MER,
            n_azimuthal=N_AZ,
        )
        print("done.")
    return _mesh


# ---------------------------------------------------------------------------
# View openers
# ---------------------------------------------------------------------------

def _open_view(view_key: str) -> None:
    """Open the plot corresponding to view_key in a new figure window."""

    if view_key == "2d":
        plot_cross_section_validation(D, R_c, r_k, t, h)

    elif view_key == "simple":
        mesh = _get_mesh()
        fig  = plt.figure(figsize=(9, 7))
        ax   = fig.add_subplot(111, projection="3d")
        plot_3d_head(mesh, ax,
                     zone_colors=False,
                     alpha=0.80,
                     stride=STRIDE)
        ax.set_title(
            "3D Simple — single colour\n"
            f"D={D:.0f}  Rc={R_c:.0f}  rk={r_k:.0f}  t={t:.0f}  h={h:.0f}  (mm)"
        )
        fig.canvas.manager.set_window_title("Torosphere — 3D Simple")

    elif view_key == "zones":
        mesh = _get_mesh()
        fig  = plt.figure(figsize=(9, 8))
        ax   = fig.add_subplot(111, projection="3d")
        plot_3d_head(mesh, ax,
                     zone_colors=True,
                     alpha=0.88,
                     stride=STRIDE)
        ax.set_title(
            "3D Zone-Coloured — cross-reference with 2D validation\n"
            f"D={D:.0f}  Rc={R_c:.0f}  rk={r_k:.0f}  t={t:.0f}  h={h:.0f}  (mm)"
        )
        legend_handles = [
            Patch(facecolor=color, label=f"{i + 1}. {name}", alpha=0.9)
            for i, (name, color) in enumerate(SEGMENT_COLORS.items())
        ]
        fig.legend(handles=legend_handles,
                   loc="lower center", ncol=4,
                   fontsize=8.5, framealpha=0.93,
                   bbox_to_anchor=(0.5, 0.01))
        fig.subplots_adjust(bottom=0.19)
        fig.canvas.manager.set_window_title("Torosphere — 3D Zone-Coloured")

    elif view_key == "half":
        mesh = _get_mesh()
        fig  = plt.figure(figsize=(9, 8))
        ax   = fig.add_subplot(111, projection="3d")
        plot_3d_head(mesh, ax,
                     half_section=True,
                     show_cut_face=True,
                     zone_colors=True,
                     alpha=0.88,
                     elev=22, azim=15,
                     stride=STRIDE)
        ax.set_title(
            "3D Half-Section — wall thickness visible at cut plane\n"
            f"D={D:.0f}  Rc={R_c:.0f}  rk={r_k:.0f}  t={t:.0f}  h={h:.0f}  (mm)"
        )
        legend_handles = [
            Patch(facecolor=color, label=f"{i + 1}. {name}", alpha=0.9)
            for i, (name, color) in enumerate(SEGMENT_COLORS.items())
        ] + [
            Patch(facecolor=CUT_FACE_COLOR, edgecolor=CUT_FACE_EDGE,
                  label="9. Cut face (wall cross-section)"),
        ]
        fig.legend(handles=legend_handles,
                   loc="lower center", ncol=3,
                   fontsize=8.5, framealpha=0.93,
                   bbox_to_anchor=(0.5, 0.01))
        fig.subplots_adjust(bottom=0.22)
        fig.canvas.manager.set_window_title("Torosphere — 3D Half-Section")


# ---------------------------------------------------------------------------
# Launcher window builder
# ---------------------------------------------------------------------------

def _build_launcher() -> tuple[plt.Figure, list[Button]]:
    """Create and return the launcher figure and button list.

    The button list is returned so the caller can keep references alive.
    (Python's garbage collector will destroy the buttons — and their click
    handlers — if nothing holds a reference to them.)
    """
    fig = plt.figure(figsize=(5, 5.2))
    fig.patch.set_facecolor("#f0f4fb")
    fig.canvas.manager.set_window_title("Torosphere — Launcher")

    # Title
    fig.text(
        0.5, 0.93,
        "Torospherical Head Visualizer",
        ha="center", va="top",
        fontsize=14, fontweight="bold", color="#1a2a4a",
    )

    # Parameter summary
    fig.text(
        0.5, 0.84,
        f"D = {D:.0f}   Rc = {R_c:.0f}   rk = {r_k:.0f}   t = {t:.0f}   h = {h:.0f}   (mm)",
        ha="center", va="top",
        fontsize=9, color="#555555",
    )

    # Divider line
    fig.text(0.5, 0.78, "─" * 48, ha="center", va="top",
             fontsize=7, color="#aaaaaa")

    # Instruction
    fig.text(
        0.5, 0.74,
        "Click a button to open a view.\n"
        "Close the view window to return here.",
        ha="center", va="top",
        fontsize=8.5, color="#666666",
    )

    # ── Buttons ───────────────────────────────────────────────────────────
    # Positions: [left, bottom, width, height] in figure coordinates (0–1).
    # Four buttons evenly spaced between y = 0.17 and y = 0.60.
    btn_h    = 0.095
    btn_gap  = 0.020
    btn_ybot = 0.17   # y of the bottom button
    btn_l, btn_w = 0.10, 0.80

    buttons: list[Button] = []
    selection: list[str | None] = [None]   # mutable container for callback

    for i, (label, view_key) in enumerate(_BUTTONS):
        y = btn_ybot + (len(_BUTTONS) - 1 - i) * (btn_h + btn_gap)
        ax_btn = fig.add_axes([btn_l, y, btn_w, btn_h])
        btn = Button(ax_btn, label,
                     color=_BTN_COLOR, hovercolor=_BTN_HOVER_COLOR)
        btn.label.set_fontsize(10)
        btn.label.set_color("#1a2a4a")

        # Closure: capture view_key for this iteration
        def make_cb(key: str):
            def cb(event):
                selection[0] = key
                plt.close(fig)      # closes launcher → plt.show() returns
            return cb

        btn.on_clicked(make_cb(view_key))
        buttons.append(btn)   # keep reference alive

    # Footer note
    fig.text(
        0.5, 0.05,
        f"Mesh: n_meridional={N_MER}  n_azimuthal={N_AZ}  stride={STRIDE}",
        ha="center", va="bottom",
        fontsize=7.5, color="#999999",
    )

    return fig, buttons, selection


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def launch_gui() -> None:
    """Run the launcher GUI.

    This is a blocking call — it returns only when the launcher window is
    closed without selecting a view (i.e. the user is done).

    The flow is a simple modal loop:
        while True:
            show launcher  (blocking)
            if user closed without clicking  → break
            open selected plot               (blocking)
            ↑ loops back to launcher
    """
    while True:
        fig, buttons, selection = _build_launcher()
        plt.show()   # ← blocks until launcher fig is closed

        if selection[0] is None:
            # User closed the launcher window directly — exit
            break

        _open_view(selection[0])
        plt.show()   # ← blocks until the plot window is closed
        # Loop: launcher will reopen


if __name__ == "__main__":
    launch_gui()
