import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sphere.spherical_map import make_initial_map
from sphere.renderer import SphereRenderer

smap = make_initial_map()
r = SphereRenderer(smap)
r.plotter.show()
