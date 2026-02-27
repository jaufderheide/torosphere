@import "style.less"

# Step 1: Cross-Section Definition

## Coordinate System

| Axis | Origin | Positive direction |
|------|--------|--------------------|
| $r$ | centreline | radially outward |
| $z$ | bottom of straight flange (open end) | toward dome apex |

The cross-section profile lives in the $r \geq 0$ half of the $r$–$z$ plane.

## Input Parameters

| Symbol | Name | Constraint |
|--------|------|------------|
| $D$ | Inside diameter | $D > 0$ |
| $R_c$ | Crown radius (inner) | $R_c \geq D/2$ |
| $r_k$ | Knuckle radius (inner) | $t < r_k < D/2$ |
| $t$ | Shell thickness | $0 < t < r_k$ |
| $h$ | Straight flange height | $h \geq 0$ |

## Derived Geometry

**Knuckle sweep angle** (same for inner and outer — a consequence of uniform normal thickness):

$$\alpha = \arccos\!\left(\frac{D/2 - r_k}{R_c - r_k}\right)$$

**Crown sphere centre** (on axis, may be at negative $z$):

$$z_{sc} = h - \sqrt{(R_c - r_k)^2 - (D/2 - r_k)^2}$$

Sphere centre coordinates: $(0,\ z_{sc})$

> ⚠️ **Note:** $z_{sc}$ is frequently **negative** for typical proportions (e.g. $R_c = D$). The sphere centre lies below the flange base — only a shallow cap of the large sphere is used for the dome. This is geometrically correct.

**Knuckle arc centres** (inner and outer share the same centre — uniform normal offset property):

$$(r_{kc},\ z_{kc}) = (D/2 - r_k,\ h)$$

**Crown–knuckle tangency point (inner):**

$$r_t = \frac{R_c\,(D/2 - r_k)}{R_c - r_k}, \qquad z_t = z_{sc} + \sqrt{R_c^2 - r_t^2}$$

**Crown–knuckle tangency point (outer):**

$$r_{t,\text{out}} = \frac{(R_c+t)\,(D/2 - r_k)}{R_c - r_k}, \qquad z_{t,\text{out}} = z_{sc} + \sqrt{(R_c+t)^2 - r_{t,\text{out}}^2}$$

**Apex heights:**

$$z_{\text{apex,inner}} = z_{sc} + R_c, \qquad z_{\text{apex,outer}} = z_{sc} + R_c + t$$

**Crown arc polar angles** (measured from $+z$ axis at sphere centre, so $\phi=0$ is the apex):

$$\phi_t = \arcsin\!\left(\frac{r_t}{R_c}\right)$$

Note that $\phi_t = \arcsin(\text{ratio})$ and $\alpha = \arccos(\text{ratio})$ where $\text{ratio} = (D/2-r_k)/(R_c-r_k)$.
Therefore $\alpha + \phi_t = \pi/2$ — they are **complementary angles**, which enforces tangent-direction continuity at the crown–knuckle junction.

The outer tangency angle is identical: $\phi_{t,\text{out}} = \phi_t$. This follows from the parallel-curve property (both arc centres are the same for inner and outer).

---

## Closed Profile Segments

Traversed counter-clockwise (inward surface first, outward surface back) starting at the inner apex. This produces a closed, simply-connected region whose revolution generates the solid.

| # | Segment | Parametric equations | Parameter range |
|---|---------|----------------------|-----------------|
| 1 | Inner crown arc | $r = R_c \sin\phi,\quad z = z_{sc} + R_c \cos\phi$ | $\phi: 0 \to \phi_t$ |
| 2 | Inner knuckle arc | $r = (D/2 - r_k) + r_k\cos\theta,\quad z = h + r_k\sin\theta$ | $\theta: \alpha \to 0$ |
| 3 | Inner straight flange | $r = D/2,\quad z: h \to 0$ | — |
| 4 | Bottom rim | $z = 0,\quad r: D/2 \to D/2 + t$ | — |
| 5 | Outer straight flange | $r = D/2 + t,\quad z: 0 \to h$ | — |
| 6 | Outer knuckle arc | $r = (D/2 - r_k) + (r_k+t)\cos\theta,\quad z = h + (r_k+t)\sin\theta$ | $\theta: 0 \to \alpha$ |
| 7 | Outer crown arc | $r = (R_c+t)\sin\phi,\quad z = z_{sc} + (R_c+t)\cos\phi$ | $\phi: \phi_t \to 0$ |
| 8 | Apex flat | $r = 0,\quad z: z_{\text{apex,outer}} \to z_{\text{apex,inner}}$ | — |

> **Tangency check:** At the junction of segments 1↔2 and 6↔7 the arc tangent directions must be continuous. This is guaranteed analytically by the derivation of $\alpha$ and $z_{sc}$ above — no special handling needed in code.

---

## Validation Constraints

Before computing any geometry, raise a clear error if:

| # | Condition | Reason |
|---|-----------|--------|
| 1 | $r_k \geq D/2$ | Knuckle doesn't fit within the bore |
| 2 | $R_c < D/2$ | Crown sphere can't span the bore |
| 3 | $t \geq r_k$ | Outer knuckle would self-intersect |
| 4 | $(D/2 - r_k)/(R_c - r_k) \geq 1$ | $\arccos$ argument $\geq 1$: no real solution |
| 5 | $h < 0$ | Non-physical flange height |

---
