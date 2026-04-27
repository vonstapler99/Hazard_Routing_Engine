"""
Phase 2 — step 1: download OSM for the Phase 1 bbox and print graph statistics.

Run from repo root (needs network access to the Overpass API):

    python scripts/inspect_osm_graph.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from routing.osm_graph import load_drive_network, study_bbox_for_osmnx


def main() -> None:
    bbox = study_bbox_for_osmnx()
    print("OSMnx bbox (west, south, east, north) as (left, bottom, right, top):")
    print(f"  {bbox[0]:.8f}, {bbox[1]:.8f}, {bbox[2]:.8f}, {bbox[3]:.8f}")
    print("Downloading graph (Overpass) ...")
    G = load_drive_network()
    # MultiDiGraph: parallel edges allowed (e.g. separate lanes); |V| and |E| are standard size checks.
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    print(f"Graph: {n_nodes} nodes, {n_edges} directed edges (MultiDiGraph)")
    crs = G.graph.get("crs", "(not set on graph)")
    print("Graph CRS metadata:", crs)


if __name__ == "__main__":
    main()
