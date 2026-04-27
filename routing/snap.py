"""
Map real-world A/B coordinates onto the OSM graph (Phase 2, before A*).

**Why transform first:** Our routing graph lives in a projected CRS (UTM meters).
You naturally specify stops as WGS84 latitude/longitude. Mixing degrees with
node ``x``/``y`` in meters would break distance logic, so we project the
query point into the graph CRS, then find the closest node in that plane.

**Why Euclidean on projected nodes:** Over ~2 miles, UTM distortion is small;
nearest-node in meter space is standard for OSMnx-style workflows. The snap
error is the straight-line gap from your true point to the intersection node.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from pyproj import Transformer

if TYPE_CHECKING:
    import networkx as nx


def wgs84_latlon_to_graph_xy(
    lat: float,
    lon: float,
    graph_crs: str | object,
) -> tuple[float, float]:
    """
    Convert WGS84 (EPSG:4326) to the graph's projected coordinates.

    ``always_xy=True`` keeps (lon, lat) order for the geographic side, matching
    GeoJSON / PROJ conventions even though the Python parameters are named lat/lon.
    """
    transformer = Transformer.from_crs("EPSG:4326", graph_crs, always_xy=True)
    x, y = transformer.transform(float(lon), float(lat))
    return float(x), float(y)


def snap_latlon_to_nearest_node(
    G: nx.MultiDiGraph,
    lat: float,
    lon: float,
) -> tuple[int, float]:
    """
    Nearest graph node to a WGS84 point.

    Returns ``(node_id, distance_m)`` where distance is planar Euclidean distance
    in the graph CRS (meters for UTM). We scan all nodes with NumPy instead of
    ``osmnx.distance.nearest_nodes`` so we do not require **scipy** (optional for
    OSMnx on projected graphs).
    """
    crs = G.graph["crs"]
    x, y = wgs84_latlon_to_graph_xy(lat, lon, crs)

    node_list = list(G.nodes)
    coords = np.array(
        [[G.nodes[n]["x"], G.nodes[n]["y"]] for n in node_list],
        dtype=np.float64,
    )
    dx = coords[:, 0] - x
    dy = coords[:, 1] - y
    d2 = dx * dx + dy * dy
    i = int(np.argmin(d2))
    dist_m = float(math.sqrt(float(d2[i])))
    return int(node_list[i]), dist_m


def snap_endpoint_pair_wgs84(
    G: nx.MultiDiGraph,
    lat_a: float,
    lon_a: float,
    lat_b: float,
    lon_b: float,
) -> tuple[tuple[int, float], tuple[int, float]]:
    """Snap two WGS84 endpoints; returns ``((node_a, dist_a), (node_b, dist_b))``."""
    snap_a = snap_latlon_to_nearest_node(G, lat_a, lon_a)
    snap_b = snap_latlon_to_nearest_node(G, lat_b, lon_b)
    return snap_a, snap_b
