@import "style.less"

# Torospherical Head Visualization — Project Overview

A torospherical head is a **surface of revolution** — the correct approach is to define a
closed 2D cross-section profile and rotate it 360° around the centreline axis.  Using a
closed profile (rather than just the inner surface) encloses the full material wall, making
the 3D result visualizable as a true solid rather than an infinitely thin shell.

---

## Geometry Summary

The profile consists of **8 segments** traversed counter-clockwise from the inner crown apex
back to the outer crown apex:

| # | Segment | Geometry |
|---|---------|----------|
| 1 | **Inner crown arc** | Spherical arc, radius $R_c$, centre at $(0,\ z_{sc})$ |
| 2 | **Inner knuckle arc** | Toroidal arc, radius $r_k$, ring centre at $(D/2 - r_k,\ z_{tc})$ |
| 3 | **Inner straight flange** | Vertical line at $r = D/2$, from knuckle tangency down to $z = 0$ |
| 4 | **Bottom rim** | Horizontal line at $z = 0$ from $r = D/2$ to $r = D/2 + t$ |
| 5 | **Outer straight flange** | Vertical line at $r = D/2 + t$, from $z = 0$ up to knuckle tangency |
| 6 | **Outer knuckle arc** | Toroidal arc, radius $r_k + t$, same ring centre as inner |
| 7 | **Outer crown arc** | Spherical arc, radius $R_c + t$, same centre as inner |
| 8 | **Apex flat** | Horizontal line at the dome apex connecting outer and inner crown |

The key derived quantity is the **crown sphere centre** $z_{sc}$, which enforces tangency
between the crown sphere and the knuckle torus:

$$z_{sc} = h - \sqrt{(R_c - r_k)^2 - (D/2 - r_k)^2}$$

> ⚠️ **Note:** $z_{sc}$ is frequently **negative** for typical ASME proportions ($R_c = D$,
> $r_k = 0.1D$). The sphere centre lies below the flange base — only a shallow spherical cap
> is used for the dome.  This is geometrically correct and expected.

> **ASME proportion guidance:** The ASME standard typically uses $R_c = D$ and $r_k = 0.1D$
> as a common design proportion, with $r_k \geq 0.06D$ as the practical minimum. This tool
> does not enforce these ratios — it will correctly visualize any geometrically valid
> combination.  ASME compliance is the responsibility of the design calculation software that
> this tool is intended to supplement.

**Coordinate convention:** $z = 0$ at the open (flange) end, $z$ increases toward the apex.
$r = 0$ on the centreline axis.

---

## Project Structure

| File | Role |
|------|------|
| `geometry.py` | Pure geometry — inputs → derived quantities → closed $(r, z)$ profile arrays |
| `mesh_3d.py` | Pure geometry — revolves the profile into a structured 3D mesh |
| `visualization_2d.py` | Annotated 2D cross-section validation plot |
| `visualization_3d.py` | 3D surface plots (zone-coloured, half-section, single-colour) |
| `gui.py` | Launcher GUI — one view at a time for interactive performance |
| `main.py` | Entry point — calls `launch_gui()` |

### Key design decisions implemented

- **Geometry is fully decoupled from plotting.**  `geometry.py` and `mesh_3d.py` have no
  matplotlib dependency; they can be imported and used independently for export or further
  computation.

- **Input validation** in `geometry.py` checks all eight geometric constraints (e.g.
  $r_k < D/2$, $R_c \geq D/2$, $t < r_k$) and raises a descriptive `ValueError` before any
  geometry is computed.

- **Parameterised mesh resolution** — `build_head_mesh()` accepts `n_meridional` and
  `n_azimuthal` arguments.  The GUI defaults to moderate values (`N_MER=64`, `N_AZ=60`) with
  `STRIDE=2` for fast interactive response; increase these for publication-quality renders.

- **Equal-axis scaling** — matplotlib's 3D axes do not enforce equal scales by default.
  `_set_equal_aspect()` in `visualization_3d.py` uses `ax.set_box_aspect()` to match the
  rendered box dimensions to the actual physical extents.

- **One-at-a-time GUI** — rendering all views simultaneously caused noticeable lag even on
  high-end hardware.  The launcher uses a modal loop (show launcher → user picks a view →
  show plot → close → back to launcher) so only one plot is ever alive at a time.

---

## Step Documentation

Each implementation step is documented in its own file:

| Step | Document | Content |
|------|----------|---------|
| 1 | [step1_cross_section_definition.md](step1_cross_section_definition.md) | Coordinate system, inputs, derived geometry formulas, 8-segment table, validation constraints |
| 2 | [step2_cross_section_implementation.md](step2_cross_section_implementation.md) | `geometry.py` API, angle conventions, junction deduplication, apex flat, $z_{sc}$ negativity |
| 2b | [step2b_2d_validation.md](step2b_2d_validation.md) | `visualization_2d.py` API, 8-item validation checklist, reference test case |
| 3 | [step3_3d_mesh_generation.md](step3_3d_mesh_generation.md) | Revolution operation, grid structure, closure properties, `HeadMesh` fields, density guidance |
| 4 | [step4_visualization.md](step4_visualization.md) | Zone colouring, half-section mechanism, equal-aspect fix, `segment_row_ranges()` index table, full file summary |

---

## Running the Project

```bash
# From the project root, with the virtual environment active:
python main.py
```

This opens the launcher window.  Choose a view, close it to return to the launcher, and close
the launcher to exit.  To change the head geometry, edit the constants at the top of `gui.py`.


