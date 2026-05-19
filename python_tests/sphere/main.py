import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import argparse
from sphere.spherical_map import make_initial_map
from sphere.renderer import SphereRenderer
from sphere.interaction import InteractionController


def main():
    parser = argparse.ArgumentParser(description="Sphere Map Explorer")
    parser.add_argument("--auto", type=int, default=0,
                        help="Run N automatic splits then show")
    parser.add_argument("--strategy", default="balanced",
                        choices=["balanced", "random"])
    args = parser.parse_args()

    smap = make_initial_map()
    renderer = SphereRenderer(smap)

    if args.auto > 0:
        from sphere.spherical_map import grow_map
        grow_map(smap, renderer, n_splits=args.auto,
                 strategy=args.strategy, show=True)
    else:
        ctrl = InteractionController(smap, renderer)

    renderer.plotter.add_text(
        "Sphere Map Explorer", position="lower_left",
        font_size=9, color="gray",
    )
    renderer.plotter.show(title="Sphere Map Explorer")


if __name__ == "__main__":
    main()
