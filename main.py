"""
Torosphere - Main entry point

Launches the interactive GUI. Four views are available — choose one at a
time from the launcher window:

  1 — 2D Cross-Section Validation
  2 — 3D Simple (single colour)
  3 — 3D Zone-Coloured
  4 — 3D Half-Section + Cutaway

To change the head geometry, edit the parameters at the top of gui.py.
"""

from gui import launch_gui

if __name__ == "__main__":
    launch_gui()




