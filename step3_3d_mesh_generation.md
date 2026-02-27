@import "style.less"
# Step 3: 3D Mesh Generation

## Overview

The 2D cross-section profile produced in Step 2 is revolved 360° around the
z-axis (the centreline) to produce a structured 3D surface mesh. The output
is a pair of 2D grids `(rows × columns)` that can be fed directly to
`matplotlib`'s `plot_surface`, or converted to face/vertex lists for export.

---

## File: `mesh_3d.py`

### Public API

| Symbol | Type | Purpose |
|--------|------|---------|
| `HeadMesh` | frozen `@dataclass` | Grid arrays + metadata for the completed mesh |
| `revolve_profile(r, z, n_az)` | `→ (X, Y, Z, theta)` | Core revolution operation |
| `build_head_mesh(D, R_c, r_k, t, h, n_meridional, n_azimuthal)` | `→ HeadMesh` | Full pipeline: validate → profile → revolve → package |

---

## The Revolution Operation

Each point $(r_i, z_i)$ in the profile is revolved through azimuthal angles
$\theta_j \in [0, 2\pi]$ to produce:

$$X_{ij} = r_i \cos\theta_j, \qquad Y_{ij} = r_i \sin\theta_j, \qquad Z_{ij} = z_i$$

Implemented as outer products — no Python loops:

```python
theta = np.linspace(0, 2π, n_az + 1)
X = np.outer(r, np.cos(theta))   # shape (N_profile, n_az+1)
Y = np.outer(r, np.sin(theta))
Z = np.outer(z, np.ones(n_az+1))
```

---

## Grid Structure

```
         θ₀   θ₁   θ₂  ...  θ_{n_az}=2π
        ┌────┬────┬────┬────┬────┐
row 0   │ inner apex (r=0, z=z_apex_inner)    ← pole (degenerate)
        ├────┼────┼────┼────┼────┤
row 1   │  inner crown arc ...
        ├────┼    ...
        ├────┤
row k   │  inner knuckle arc
        ├────┤
row k+1 │  inner flange
        ├────┤
row k+2 │  bottom rim
        ├────┤
row k+3 │  outer flange
        ├────┤
row k+4 │  outer knuckle arc
        ├────┤
row k+5 │  outer crown arc
        ├────┤
row N-2 │ outer apex (r=0, z=z_apex_outer)   ← pole (degenerate)
        ├────┤
row N-1 │ = row 0  (profile closure)
        └────┴────┴────┴────┴────┘
         col0                col n_az
         (θ=0)             (θ=2π ≡ θ=0)
```

- **Axis 0 (rows)** — meridional direction (along the cross-section profile)
- **Axis 1 (columns)** — azimuthal direction (angle θ around the axis)
- `X.shape = (n_profile, n_azimuthal + 1)`

---

## Closure Properties

| Property | How it is achieved |
|----------|-------------------|
| Azimuthal closure (no seam gap) | `theta[-1] = 2π` so `X[:, -1] = X[:, 0]`, `Y[:, -1] = Y[:, 0]` |
| Meridional closure (sealed solid) | Profile is closed — `r[0]=r[-1]`, `z[0]=z[-1]` — so `row 0 = row N-1` |
| Apex poles | Rows where `r[i] = 0` collapse to a single 3D point; all `X[i,:]` and `Y[i,:]` are zero |

---

## Degenerate Pole Rows

Two rows have `r = 0`:

| Row | z-coordinate | Description |
|-----|-------------|-------------|
| Inner apex | `z_apex_inner = z_sc + R_c` | Dome apex, inner surface |
| Outer apex | `z_apex_outer = z_sc + R_c + t` | Dome apex, outer surface |

At these rows every azimuthal column maps to the same 3D point
$(0, 0, z_\text{apex})$. `matplotlib`'s `plot_surface` renders them as
collapsed triangles (zero area) without errors. Subtle lighting artefacts
may appear near the poles — these are addressed in Step 4's visualization.

---

## `HeadMesh` Fields

| Field | Shape / Type | Description |
|-------|-------------|-------------|
| `X` | `(n_profile, n_az+1)` | Cartesian x-coordinates |
| `Y` | `(n_profile, n_az+1)` | Cartesian y-coordinates |
| `Z` | `(n_profile, n_az+1)` | Cartesian z-coordinates |
| `r` | `(n_profile,)` | Source profile r-coordinates |
| `z_profile` | `(n_profile,)` | Source profile z-coordinates |
| `theta` | `(n_az+1,)` | Azimuthal angles (radians) |
| `geometry` | `HeadGeometry` | All derived geometric quantities |
| `n_meridional` | `int` | Arc samples per segment used |
| `n_azimuthal` | `int` | Azimuthal subdivisions used |

Convenience properties: `n_profile`, `n_quads`, `z_min`, `z_max`, `r_max`.

---

## Mesh Density Guidance

| Use case | `n_meridional` | `n_azimuthal` | Approx. quads |
|----------|---------------|--------------|--------------|
| Quick validation | 32 | 36 | ~5 500 |
| Interactive display | 128 | 90 | ~87 000 |
| High-quality render | 256 | 180 | ~348 000 |

`n_meridional` controls smoothness of the dome–knuckle transition.
`n_azimuthal` controls roundness of the circular cross-sections.
For non-circular display artefacts (flat facets), increase `n_azimuthal` first.

---

## Step 3 Sanity Check

`main.py` runs the following checks and a basic surface plot:

| Check | Expected |
|-------|---------|
| `X.shape` | `(n_profile, n_azimuthal + 1)` |
| `Z` range | `[0.0, z_apex_outer]` mm |
| `r_max` | `D/2 + t` mm |
| `theta[-1]` | `2π` (6.2832…) |
| `X[:, 0] ≈ X[:, -1]` | True (azimuthal seam closed) |

---
