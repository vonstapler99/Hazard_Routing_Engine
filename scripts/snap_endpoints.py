"""
Demonstrate snapping two WGS84 points (A and B) to nearest drive-network nodes.

Run from repo root:

    python scripts/snap_endpoints.py

Adjust LAT_A / LON_A / LAT_B / LON_B to your scenario; keep points inside the
Phase 1 study bbox so the graph contains nearby roads.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from routing.osm_graph import load_projected_drive_network
from routing.snap import snap_endpoint_pair_wgs84, wgs84_latlon_to_graph_xy

# Example endpoints near Kerrville center (tweak as needed).
LAT_A, LON_A = 30.0550, -99.1500
LAT_B, LON_B = 30.0480, -99.1380


def main() -> None:
    G = load_projected_drive_network()
    print("Projected CRS:", G.graph.get("crs"))
    print()

    for label, lat, lon in [("A", LAT_A, LON_A), ("B", LAT_B, LON_B)]:
        x, y = wgs84_latlon_to_graph_xy(lat, lon, G.graph["crs"])
        print(f"{label} WGS84: lat={lat:.6f}, lon={lon:.6f}")
        print(f"  projected (x, y) m: {x:.2f}, {y:.2f}")

    (na, da), (nb, db) = snap_endpoint_pair_wgs84(G, LAT_A, LON_A, LAT_B, LON_B)
    print()
    print(f"Nearest node to A: {na}  (snap offset {da:.2f} m)")
    print(f"Nearest node to B: {nb}  (snap offset {db:.2f} m)")
    print()
    print("Node A coords (projected):", G.nodes[na]["x"], G.nodes[na]["y"])
    print("Node B coords (projected):", G.nodes[nb]["x"], G.nodes[nb]["y"])


if __name__ == "__main__":
    main()
