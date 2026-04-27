"""
Print the Phase 1 study bounding box and quick geodesic sanity checks.

Run from the repository root:
    python scripts/print_bbox.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `from data.config import ...` without installing the repo as a package.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pyproj import Geod

from data.config import (
    CENTER_LAT,
    CENTER_LON,
    HALF_EXTENT_METERS,
    STATUTE_MILE_METERS,
    study_area_bbox_wgs84,
)


def main() -> None:
    north, south, east, west = study_area_bbox_wgs84()
    print("Study center (WGS84):", CENTER_LAT, CENTER_LON)
    print("Half-extent (m):", HALF_EXTENT_METERS)
    print("OSMnx-style bbox (north, south, east, west):")
    print(f"  {north:.8f}, {south:.8f}, {east:.8f}, {west:.8f}")

    # Geod.inv solves the inverse geodesic: great-circle distance between two
    # (lon, lat) pairs on the ellipsoid — good for "how wide is our window?"
    geod = Geod(ellps="WGS84")
    # Meridional span through the center longitude (north–south "height").
    _, _, dist_ns = geod.inv(CENTER_LON, south, CENTER_LON, north)
    # Parallel-ish span through the center latitude (east–west "width").
    _, _, dist_ew = geod.inv(west, CENTER_LAT, east, CENTER_LAT)

    print("\nGeodesic edge-to-edge at center lines (meters):")
    print(f"  N-S through center lon: {dist_ns:.2f} (~{dist_ns / STATUTE_MILE_METERS:.3f} mi)")
    print(f"  E-W through center lat: {dist_ew:.2f} (~{dist_ew / STATUTE_MILE_METERS:.3f} mi)")
    print("  (Expect ~2 statute miles each if half-extent is 1 mi.)")


if __name__ == "__main__":
    main()
