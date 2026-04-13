"""
Plot the drivable OSM street graph for the Phase 1 study bbox.

`ox.plot_graph` draws edges as polylines in WGS84 (lon/lat) and nodes as scatter
points on top — a quick sanity check that download + bbox look reasonable.

Run from repo root (needs network unless OSMnx cache already has the bbox):

    python scripts/plot_graph.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import matplotlib.pyplot as plt
import osmnx as ox

from routing.osm_graph import load_drive_network


def main() -> None:
    print("Loading drive network (Overpass or cache) ...")
    G = load_drive_network()

    # High-contrast styling so nodes (intersections) read clearly over edges.
    # `show=True` (default) opens an interactive window; axis units are degrees.
    ox.plot_graph(
        G,
        bgcolor="#f7f7f7",
        node_color="#c0392b",
        node_size=25,
        node_edgecolor="white",
        node_zorder=2,
        edge_color="#34495e",
        edge_linewidth=0.8,
        figsize=(10, 10),
        show=False,
    )
    plt.title("Study area: drivable OSM network (nodes + edges)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
