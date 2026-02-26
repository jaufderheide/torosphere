# Step 2: Cross-Section Implementation

## Overview

This step implements `geometry.py` — the pure-geometry module that produces
the closed 2D cross-section profile from the five input parameters.
No plotting code lives here; it returns NumPy arrays only.

---

## File: `geometry.py`

### Public API

| Symbol | Type | Purpose |
|--------|------|---------|
| `HeadGeometry` | frozen `@dataclass` | Holds all derived quantities from the inputs |
| `validate_inputs(D, R_c, r_k, t, h)` | `→ None` | Raises `ValueError` on any constraint violation |
| `compute_derived_geometry(D, R_c, r_k, t, h)` | `→ HeadGeometry` | Computes all derived geometry (calls validate) |
| `build_cross_section(D, R_c, r_k, t, h, n_arc)` | `→ (r, z)` | Full closed profile as NumPy arrays |

---

## Key Implementation Decisions

### 1. Angle conventions

Two independent angle parameters are used and are **complementary** ($\alpha + \phi_t = \pi/2$):

| Symbol | Where | Definition |
|--------|-------|------------|
| $\phi$ | Crown arc | Polar angle from the $+z$ axis at the sphere centre. $\phi = 0$ at the apex. |
| $\theta$ | Knuckle arc | Angle from the positive-$r$ axis at the knuckle centre. $\theta = 0$ at the flange junction. |

The shared ratio:
$$\text{ratio} = \frac{D/2 - r_k}{R_c - r_k}$$

gives both:
$$\alpha = \arccos(\text{ratio}), \qquad \phi_t = \arcsin(\text{ratio})$$

This relationship is not a coincidence — it enforces the **tangent-direction continuity** ($G^1$) at the crown–knuckle junction.

### 2. Inner and outer arcs share the same centre points

The outer arcs (radius $R_c + t$, $r_k + t$) use the **exact same centre points** as the inner arcs. This is the uniform normal-offset (parallel curve) property of circles. As a consequence:
- $\alpha$ and $\phi_t$ are **identical** for inner and outer surfaces
- No separate angle computation is needed for the outer surface

### 3. Junction de-duplication

Each arc/segment is sampled with its **last point dropped** (`arr[:-1]`) before concatenation. This prevents doubled vertices at every junction point. The very last segment (apex flat) retains its end point, then the profile is explicitly closed by appending `r[0], z[0]`.

### 4. Apex flat segment

At $r = 0$, both the inner and outer crown arcs terminate on the symmetry axis at different $z$ values ($z_\text{apex,inner}$ and $z_\text{apex,outer}$ respectively). The apex flat segment connects them:

$$r = 0, \quad z \in [z_\text{apex,outer},\ z_\text{apex,inner}]$$

In 2D this is a short vertical line on the axis. When revolved (Step 3) this is a degenerate ring of zero radius — it contributes no surface area but is required to close the 2D profile.

### 5. z_sc can be (and usually is) negative

For typical ASME proportions ($R_c = D$, $r_k = 0.1D$):

$$z_{sc} \approx h - 0.806 \cdot D$$

For $D = 1000$ mm and $h = 50$ mm this gives $z_{sc} \approx -756$ mm. Only a shallow cap of the large sphere is used for the dome. The code handles this correctly and naturally.

---

## Segment Map (for `build_cross_section`)

Traversal is counter-clockwise in the $(r, z)$ half-plane.

| # | Segment | Parameter range | Geometry |
|---|---------|----------------|----------|
| 1 | Inner crown arc | $\phi: 0 \to \phi_t$ | sphere radius $R_c$, centre $(0, z_{sc})$ |
| 2 | Inner knuckle arc | $\theta: \alpha \to 0$ | circle radius $r_k$, centre $(D/2-r_k,\ h)$ |
| 3 | Inner straight flange | $z: h \to 0$ | line at $r = D/2$ |
| 4 | Bottom rim | $r: D/2 \to D/2+t$ | line at $z = 0$ |
| 5 | Outer straight flange | $z: 0 \to h$ | line at $r = D/2+t$ |
| 6 | Outer knuckle arc | $\theta: 0 \to \alpha$ | circle radius $r_k+t$, centre $(D/2-r_k,\ h)$ |
| 7 | Outer crown arc | $\phi: \phi_t \to 0$ | sphere radius $R_c+t$, centre $(0, z_{sc})$ |
| 8 | Apex flat | $z: z_\text{apex,out} \to z_\text{apex,in}$ | line at $r = 0$ |

---

## Validation Constraints (enforced in `validate_inputs`)

| # | Condition checked | Error triggered when |
|---|-------------------|----------------------|
| 1 | $D > 0$ | Non-physical diameter |
| 2 | $t > 0$ | Non-physical thickness |
| 3 | $r_k > 0$ | Non-physical knuckle radius |
| 4 | $h \geq 0$ | Non-physical flange height |
| 5 | $R_c \geq D/2$ | Crown sphere can't span the bore |
| 6 | $r_k < D/2$ | Knuckle doesn't fit inside the bore |
| 7 | $t < r_k$ | Outer knuckle would self-intersect |
| 8 | $(D/2 - r_k) / (R_c - r_k) < 1$ | No real solution for $\alpha$ / $\phi_t$ |

---

## Testing at This Step

`main.py` is updated to plot the 2D cross-section as a visual sanity check
before proceeding to Step 3 (3D mesh generation).

Recommended test case (ASME-proportioned head):

| Parameter | Value |
|-----------|-------|
| $D$ | 1000 mm |
| $R_c$ | 1000 mm (= $D$) |
| $r_k$ | 100 mm (= 0.1$D$) |
| $t$ | 10 mm |
| $h$ | 50 mm |

Expected behaviour: smooth profile with no kinks at the crown–knuckle junctions.
The dome height above the flange should be approximately 193 mm for these values.

---
