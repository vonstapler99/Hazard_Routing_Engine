"""
Phase 2 — projected graph: print CRS, edge length stats, and a sample edge.

Run from repo root:

    python scripts/inspect_projected_graph.py
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from routing.osm_graph import load_projected_drive_network


def main() -> None:
    print("Loading + projecting drive network (Overpass or cache) ...")
    G = load_projected_drive_network()
    crs = G.graph.get("crs")
    print("Projected CRS:", crs)

    lengths = [float(d["length"]) for _, _, _, d in G.edges(keys=True, data=True)]
    print(f"Edges: {len(lengths)}")
    print(
        "length (m): min={:.2f} median={:.2f} max={:.2f}".format(
            min(lengths),
            statistics.median(lengths),
            max(lengths),
        )
    )

    # Show one edge where geometry exists so you can tie length to the polyline.
    for u, v, k, data in G.edges(keys=True, data=True):
        if data.get("geometry") is not None:
            g = data["geometry"]
            print("\nSample edge (projected meters):")
            print(f"  u,v,k = {u}, {v}, {k}")
            print(f"  length attr = {data['length']:.3f} m")
            print(f"  geometry.length = {g.length:.3f} m (should match)")
            break


if __name__ == "__main__":
    main()
