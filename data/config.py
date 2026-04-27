"""
Study-area configuration for the Hazard Routing Engine (Phase 1).

We define intent in geographic coordinates (WGS84: EPSG:4326) because that is
what OSMnx and most public datasets expect for bbox queries. A "2 mile box"
must be specified in meters on the ellipsoid, then converted to lat/lon;
treating degree steps as uniform meter steps would skew the window away from a
true square on the ground (longitude meters per degree shrinks with cos(lat)).
"""

from __future__ import annotations

from pyproj import Geod

# --- WGS84 study center (Kerrville, Texas) ---------------------------------
# Latitude / longitude are angular coordinates on the WGS84 ellipsoid, not a
# Cartesian plane; Phase 2+ projected CRS work happens after this anchor exists.
CENTER_LAT = 30.052077
CENTER_LON = -99.144659

# --- Physical window size --------------------------------------------------
# One statute mile on the ground, expressed in SI meters (NIST definition).
STATUTE_MILE_METERS = 1609.344
# Half-extent from center to each cardinal edge: 1 mi north/south/east/west
# yields an axis-aligned *geographic* box about 2 mi tall and 2 mi wide on
# the ellipsoid along those four azimuths from the center (OSMnx: north,
# south, east, west in decimal degrees).
HALF_EXTENT_METERS = 1.0 * STATUTE_MILE_METERS

# Shared geodesic calculator (WGS84); reused so we do not recreate the object.
_WGS84 = Geod(ellps="WGS84")


def bounding_box_wgs84(
    center_lat: float,
    center_lon: float,
    half_extent_m: float,
) -> tuple[float, float, float, float]:
    """
    Build (north, south, east, west) in decimal degrees for OSMnx-style APIs.

    We walk `half_extent_m` meters along four azimuths from the center:
    0° north, 180° south, 90° east, 270° west. Geod.fwd solves the direct
    geodesic problem on the ellipsoid, which is the correct inverse of "I want
    N meters in this compass direction" unlike adding fixed degree deltas.
    """
    lon0, lat0 = center_lon, center_lat
    # Azimuth is measured clockwise from north; distance is in meters.
    # Geod.fwd returns (lon2, lat2, back_azimuth_deg) on current pyproj.
    lon_n, lat_n, _ = _WGS84.fwd(lon0, lat0, 0, half_extent_m)
    lon_s, lat_s, _ = _WGS84.fwd(lon0, lat0, 180, half_extent_m)
    lon_e, lat_e, _ = _WGS84.fwd(lon0, lat0, 90, half_extent_m)
    lon_w, lat_w, _ = _WGS84.fwd(lon0, lat0, 270, half_extent_m)

    # OSMnx graph_from_bbox expects north >= south and east >= west in deg.
    north, south = lat_n, lat_s
    east, west = lon_e, lon_w
    return (north, south, east, west)


def study_area_bbox_wgs84() -> tuple[float, float, float, float]:
    """Convenience: bbox for the configured Kerrville study window."""
    return bounding_box_wgs84(CENTER_LAT, CENTER_LON, HALF_EXTENT_METERS)


if __name__ == "__main__":
    n, s, e, w = study_area_bbox_wgs84()
    print(f"Study bbox (north, south, east, west): {n:.6f}, {s:.6f}, {e:.6f}, {w:.6f}")
