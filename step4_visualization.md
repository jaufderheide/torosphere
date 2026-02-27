@import "style.less"
# Step 4: 3D Visualization

## Overview

Step 4 adds two capabilities on top of the basic surface plot from Step 3:

1. **Zone-coloured surface** — each of the 8 cross-section segments is
   rendered in its own colour, matching the colour scheme of the 2D validation
   plot (`visualization_2d.py`). This lets the viewer directly connect what
   they see in 3D to the named geometric zones in the 2D drawing.

2. **Half-section cutaway** — the mesh is clipped at the `y = 0` plane
   (showing only the `y ≥ 0` half), and the wall cross-section is drawn as a
   filled polygon on the cut plane. This reveals the shell thickness and the
   inner profile, which are invisible on a full solid view.

The output is a side-by-side figure: full view on the left, half-section on
the right.

---

## New File: `visualization_3d.py`

### Public API

| Function | Purpose |
|----------|---------|
| `plot_3d_head(mesh, ax, ...)` | Single-panel zone-coloured 3D view |
| `plot_head_comparison(mesh, ...)` | Two-panel comparison figure (full + half-section) |

Both functions accept a `HeadMesh` from `mesh_3d.build_head_mesh` and return
matplotlib objects.

---

## How Zone Colouring Works

The structured mesh grid has shape `(n_profile, n_azimuthal + 1)`.
Rows (axis 0) correspond to positions along the meridional profile; columns
(axis 1) correspond to the azimuthal revolution angle θ.

`segment_row_ranges(n_arc)` (added to `mesh_3d.py`) maps each of the 8
cross-section segment names to a `(start_row, end_row)` pair.

Each zone is then plotted as a separate `plot_surface` call:

```python
for name, r0, r1 in segment_row_ranges(mesh.n_meridional):
    ax.plot_surface(
        mesh.X[r0 : r1 + 1, :],
        mesh.Y[r0 : r1 + 1, :],
        mesh.Z[r0 : r1 + 1, :],
        color=SEGMENT_COLORS[name],
        ...
    )
```

Adjacent zones share a boundary row (the `end_row` of one zone equals the
`start_row` of the next), so there are no gaps or overlaps between colours.

### Colour cross-reference

| # | Zone | Colour |
|---|------|--------|
| 1 | Inner crown arc | Deep blue `#1565C0` |
| 2 | Inner knuckle arc | Deep green `#2E7D32` |
| 3 | Inner straight flange | Deep red `#C62828` |
| 4 | Bottom rim | Deep purple `#6A1B9A` |
| 5 | Outer straight flange | Deep orange `#E65100` |
| 6 | Outer knuckle arc | Dark teal `#006064` |
| 7 | Outer crown arc | Deep pink `#AD1457` |
| 8 | Apex flat | Blue-grey `#37474F` |

These colours are identical to `visualization_2d.SEGMENT_COLORS`.

---

## How the Half-Section Works

The azimuthal angle θ runs from 0 to 2π across `n_azimuthal + 1` columns.
Half the columns cover θ ∈ [0, π] (the `y ≥ 0` half):

```python
n_half  = mesh.n_azimuthal // 2
col_end = n_half + 1          # inclusive upper bound
# slice: mesh.X[:, 0 : col_end]   →  θ from 0 to π
```

No mesh modification is needed — it is simply a column slice of the
existing grid.

### Cut Face

The wall cross-section polygon is drawn at y = 0 using `Poly3DCollection`.
The polygon vertices come directly from the closed profile:

```python
verts = np.column_stack([r, zeros, z])  # (r[i], 0, z[i]) for each profile point
poly  = Poly3DCollection([verts], facecolor=CUT_FACE_COLOR, ...)
ax.add_collection3d(poly)
```

The polygon is drawn twice — once at x > 0 (θ = 0 face) and once at x < 0
(θ = π face) — so the full cross-section is visible from any camera angle.

---

## Equal Aspect Ratio (Review from Step 3 Fix)

Without explicit aspect correction, matplotlib stretches all three axes to
fill the same rendered box height. For a torospherical head with
D = 1524 mm and dome height ≈ 323 mm, the Z axis would appear ≈5× too tall.

The fix — applied in `_set_equal_aspect` — uses `ax.set_box_aspect`:

```python
ax.set_box_aspect((D + 2t,  D + 2t,  dome_height))
```

The same aspect is applied to both panels so they share a consistent
visual scale. This is the most important detail for making the geometry
legible — a dome with 4:1 width-to-height ratio should look flat, not
bullet-shaped.

> **Note for junior developers:** `set_box_aspect` sets the *proportions
> of the rendered 3D box*, not the axis tick spacing. The axis limits and
> tick marks are still set independently by matplotlib. This is a visual
> scaling correction, not a data transformation.

---

## `segment_row_ranges` — New Function in `mesh_3d.py`

```python
segment_row_ranges(n_arc: int) → list[tuple[str, int, int]]
```

Returns `(name, start_row, end_row)` for each segment.

The index derivation follows from the de-duplication scheme in
`build_cross_section` (see `step2_cross_section_implementation.md`):

| Segment | Start index | End index |
|---------|-------------|-----------|
| Inner crown arc | 0 | n_arc − 1 |
| Inner knuckle arc | n_arc − 1 | 2·n_arc − 2 |
| Inner straight flange | 2·n_arc − 2 | 2·n_arc − 1 |
| Bottom rim | 2·n_arc − 1 | 2·n_arc |
| Outer straight flange | 2·n_arc | 2·n_arc + 1 |
| Outer knuckle arc | 2·n_arc + 1 | 3·n_arc |
| Outer crown arc | 3·n_arc | 4·n_arc − 1 |
| Apex flat | 4·n_arc − 1 | 4·n_arc + 1 |

Verified for n_arc = 64: all 258 profile rows covered without gaps. ✓

---

## Project File Summary

At completion of Step 4 the project contains:

| File | Role |
|------|------|
| `geometry.py` | Pure geometry: validation, derived quantities, 2D profile |
| `mesh_3d.py` | Pure geometry: 3D revolution mesh + row-range map |
| `visualization_2d.py` | 2D validation plot |
| `visualization_3d.py` | 3D zone-coloured + half-section plot |
| `main.py` | Entry point |

The geometry and mesh layers have **no matplotlib dependency** — they are
pure NumPy. Only the visualization files import matplotlib. This separation
(suggested in `approach.md`) means the geometry code can be reused for
engineering calculations or export without any plotting overhead.

---
