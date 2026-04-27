"""
Phase 2 — step 1: build a NetworkX street graph from OpenStreetMap for the study bbox.

**Why OSMnx + NetworkX:** OSM is a tagged geographic graph (nodes at intersections,
edges as road centerlines). OSMnx downloads that fragment and normalizes it into a
`networkx.MultiDiGraph` where routing algorithms (A*) can run.

**CRS note:** The download uses WGS84 (degrees). For distance-based routing we
project to a local meter grid (UTM via `ox.project_graph`) and refresh `length`
from projected polylines—see `load_projected_drive_network`.
"""

from __future__ import annotations

import math

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


def project_drive_network_to_meters(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Project node coordinates and edge geometries into a suitable **projected CRS**.

    **Why:** Degrees are not a length unit; Dijkstra/A* need additive edge costs in
    meters. OSMnx chooses a UTM (or polar stereographic) zone from the graph
    bounds so planar distances approximate ground distance well over a ~2 mi box.

    After this call, node ``x`` / ``y`` and any edge ``geometry`` are in meters
    in that CRS; ``G.graph["crs"]`` records the authority code (e.g. EPSG:32614).
    """
    return ox.project_graph(G)


def recompute_edge_lengths_meters(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Set every edge's ``length`` attribute to physical length in **meters**.

    OSMnx initially fills ``length`` with great-circle chord distance on WGS84.
    On a **simplified, projected** graph, the authoritative path length is the
    Shapely ``geometry`` polyline length in the projected plane (UTM meters).

    If an edge has no ``geometry`` (rare after simplify), we use Euclidean
    distance between endpoint nodes in projected x/y—valid because those
    coordinates are already in meters.
    """
    for u, v, key, data in G.edges(keys=True, data=True):
        geom = data.get("geometry")
        if geom is not None:
            data["length"] = float(geom.length)
        else:
            xu, yu = G.nodes[u]["x"], G.nodes[u]["y"]
            xv, yv = G.nodes[v]["x"], G.nodes[v]["y"]
            data["length"] = float(math.hypot(xv - xu, yv - yu))
    return G


def load_projected_drive_network(
    *,
    simplify: bool = True,
    retain_all: bool = False,
) -> nx.MultiDiGraph:
    """
    Download the study-area drive network, project to meters, and refresh lengths.

    This is the graph you should use when edge weight = travel distance in Phase 2.
    """
    G = load_drive_network(simplify=simplify, retain_all=retain_all)
    G = project_drive_network_to_meters(G)
    recompute_edge_lengths_meters(G)
    return G
