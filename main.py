"""
Torosphere - Main entry point

Step 3 check: build the 3D mesh and display a basic surface plot to confirm
the revolution is correct before full visualization in Step 4.
"""

import matplotlib.pyplot as plt
import numpy as np

from mesh_3d import build_head_mesh

# ---------------------------------------------------------------------------
# Head parameters  (ASME-proportioned example, all dimensions in mm)
# ---------------------------------------------------------------------------
D   = 1000.0   # inside diameter
R_c = 1000.0   # crown radius (inner)
r_k =  100.0   # knuckle radius (inner)
t   =   10.0   # shell thickness
h   =   50.0   # straight flange height


def main() -> None:
    mesh = build_head_mesh(D, R_c, r_k, t, h, n_meridional=64, n_azimuthal=60)

    # --- Numerical checks ---
    print(f"Grid shape     : {mesh.X.shape}  (n_profile × n_az+1)")
    print(f"Profile points : {mesh.n_profile}")
    print(f"Quad cells     : {mesh.n_quads}")
    print(f"Z range        : [{mesh.z_min:.1f}, {mesh.z_max:.1f}] mm")
    print(f"Max radius     : {mesh.r_max:.1f} mm  (expect {D/2 + t:.1f})")
    print(f"Closed check   : theta[0]={mesh.theta[0]:.4f}, theta[-1]={mesh.theta[-1]:.4f}")
    print(f"Seam check     : X col0==colN: {np.allclose(mesh.X[:, 0], mesh.X[:, -1])}")

    # --- Basic 3D surface plot ---
    fig = plt.figure(figsize=(9, 8))
    ax  = fig.add_subplot(111, projection="3d")

    ax.plot_surface(
        mesh.X, mesh.Y, mesh.Z,
        rstride=2, cstride=2,
        color="#4a90d9", alpha=0.72,
        linewidth=0, antialiased=True,
    )

    # Equal aspect ratio: set_box_aspect takes the *relative* extent of each
    # axis so that 1 mm looks the same length in X, Y and Z.
    x_range = mesh.X.max() - mesh.X.min()   # = D + 2t
    y_range = mesh.Y.max() - mesh.Y.min()   # = D + 2t
    z_range = mesh.Z.max() - mesh.Z.min()   # ≈ dome height (much smaller)
    ax.set_box_aspect((x_range, y_range, z_range))

    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title(
        "Torospherical Head — 3D Mesh (Step 3 sanity check)\n"
        f"D={D:.0f}  R_c={R_c:.0f}  r_k={r_k:.0f}  t={t:.0f}  h={h:.0f}  (mm)"
    )
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()


