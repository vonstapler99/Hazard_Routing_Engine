"""
Phase 2 — step 1: build a NetworkX street graph from OpenStreetMap for the study bbox.

**Why OSMnx + NetworkX:** OSM is a tagged geographic graph (nodes at intersections,
edges as road centerlines). OSMnx downloads that fragment and normalizes it into a
`networkx.MultiDiGraph` where routing algorithms (A*) can run.

**CRS note (Phase 2 vs Phase 3):** Overpass / `graph_from_bbox` use WGS84 degrees.
Edge lengths for routing are typically projected to meters inside OSMnx when you
use distance-based weights; we stay in the library defaults here and only fetch.
"""

from __future__ import annotations

import networkx as nx
import osmnx as ox

from data.config import study_area_bbox_wgs84


def study_bbox_for_osmnx() -> tuple[float, float, float, float]:
    """
    Convert our study tuple into OSMnx 2.x `graph_from_bbox` layout.

    Our `study_area_bbox_wgs84()` returns (north, south, east, west) for readability
    and to match common GIS wording. OSMnx 2.x expects::

        bbox = (left, bottom, right, top)  # west, south, east, north

    so we permute coordinates once here instead of silently passing the wrong order.
    """
    north, south, east, west = study_area_bbox_wgs84()
    left, bottom, right, top = west, south, east, north
    return (left, bottom, right, top)


def load_drive_network(
    *,
    simplify: bool = True,
    retain_all: bool = False,
) -> nx.MultiDiGraph:
    """
    Download drivable public streets inside the study bounding box.

    `network_type='drive'` restricts to roads motor vehicles can typically use,
    which matches the emergency-routing story and shrinks the graph vs `all`.
    """
    bbox = study_bbox_for_osmnx()
    return ox.graph_from_bbox(
        bbox,
        network_type="drive",
        simplify=simplify,
        retain_all=retain_all,
    )
