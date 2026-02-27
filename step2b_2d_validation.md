@import "style.less"
# Step 2b: 2D Cross-Section Validation

## Purpose

Before revolving the profile into a 3D mesh (Step 3), this intermediate step
provides a visual quality gate: run `main.py` and confirm the 2D cross-section
looks geometrically correct. Any error in the parametric equations, sign
conventions, or angular ranges will show up clearly in the 2D plot — far
easier to diagnose here than in a 3D surface.

---

## New File: `visualization_2d.py`

Contains one public function:

```python
plot_cross_section_validation(D, R_c, r_k, t, h, n_arc=128)
```

### What the plot shows

| Element | Description |
|---------|-------------|
| **Colour-coded profile** | Each of the 8 segments drawn in a distinct colour (right side); grey mirror on left for visual symmetry |
| **Ghost construction arcs** | Dashed extensions of the crown sphere and knuckle torus beyond the actual segment range — the profile arcs should lie exactly on these |
| **Tangency markers** | Gold circles at the crown–knuckle junction for inner and outer surfaces |
| **Knuckle centre markers** | Black triangles at $(r_{kc}, z_{kc}) = (D/2 - r_k, h)$ with $r_k$ radius arrow |
| **$R_c$ annotation** | Arrow pointing to the midpoint of the inner crown arc, labelled with the crown radius value |
| **Dimension arrows** | Double-headed arrows for $D/2$, $t$, and $h$ |
| **Derived geometry panel** | Text box (top-left) showing $z_{sc}$, $\alpha$, $\phi_t$, tangency coordinates, and dome height |

---

## Geometry module change: `build_cross_section_segments`

A second builder function was added to `geometry.py`:

```python
build_cross_section_segments(D, R_c, r_k, t, h, n_arc)
    → (segments, HeadGeometry)
```

`segments` is a `list[tuple[str, np.ndarray, np.ndarray]]` — each element is
`(name, r_array, z_array)` for one of the 8 profile segments, with both endpoints
included (no de-duplication at junctions). This preserves segment identity for
colour mapping.

---

## Validation Checklist

Run `main.py` and verify the following before proceeding to Step 3:

| # | Check | Expected observation |
|---|-------|----------------------|
| 1 | **Profile continuity** | No visible kinks or gaps at any of the 8 segment junctions |
| 2 | **Crown–knuckle tangency** | Gold tangency markers sit exactly on the profile; no step visible at segments 1↔2 or 6↔7 |
| 3 | **Ghost arcs align** | The blue/pink dashed ghost arcs (crown sphere) and green/teal dashed arcs (knuckle torus) line up with their respective profile segments |
| 4 | **Dimension labels** | $D/2$, $t$, and $h$ annotations match the input values |
| 5 | **Derived geometry panel** | $z_{sc}$ is negative for ASME proportions; $\alpha + \phi_t = 90°$ |
| 6 | **Profile is closed** | The filled region has no open edges (top apex meets correctly) |
| 7 | **Flange is vertical** | Inner and outer straight flanges are parallel vertical lines |
| 8 | **Knuckle arcs curve upward** | The transition from vertical flange to dome curves upward and inward |

---

## Reference Test Case

| Parameter | Value | Notes |
|-----------|-------|-------|
| $D$ | 1000 mm | |
| $R_c$ | 1000 mm | = $D$ (ASME standard proportion) |
| $r_k$ | 100 mm | = $0.1 D$ (ASME standard proportion) |
| $t$ | 10 mm | = $0.01 D$ |
| $h$ | 50 mm | = $0.05 D$ |

Expected derived values:

| Quantity | Expected |
|----------|----------|
| $z_{sc}$ | −756.23 mm |
| $\alpha$ | 63.61° |
| $\phi_t$ | 26.39° |
| Dome height | 193.77 mm |

---
