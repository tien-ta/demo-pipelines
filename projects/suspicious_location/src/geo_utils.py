"""
Geographic utility functions for suspicious location detection.

This module provides geospatial calculations for location analysis.
"""

import math
from typing import Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great circle distance between two points on Earth.

    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees

    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def calculate_velocity(distance_km: float, time_hours: float) -> float:
    """
    Calculate velocity in km/h.

    Args:
        distance_km: Distance traveled in kilometers
        time_hours: Time elapsed in hours

    Returns:
        Velocity in km/h
    """
    if time_hours <= 0:
        return 0.0
    return distance_km / time_hours


def is_impossible_travel(distance_km: float, time_hours: float,
                        max_speed_kmh: float = 800.0) -> bool:
    """
    Determine if travel between two points is impossible.

    Args:
        distance_km: Distance traveled in kilometers
        time_hours: Time elapsed in hours
        max_speed_kmh: Maximum reasonable speed (default: 800 km/h for air travel)

    Returns:
        True if travel is impossible, False otherwise
    """
    if time_hours <= 0:
        return distance_km > 0  # Any distance in zero time is impossible

    velocity = calculate_velocity(distance_km, time_hours)
    return velocity > max_speed_kmh


def point_in_circle(lat: float, lon: float,
                   center_lat: float, center_lon: float,
                   radius_km: float) -> bool:
    """
    Check if a point is within a circular geofence.

    Args:
        lat: Point latitude
        lon: Point longitude
        center_lat: Circle center latitude
        center_lon: Circle center longitude
        radius_km: Circle radius in kilometers

    Returns:
        True if point is within circle, False otherwise
    """
    distance = haversine_distance(lat, lon, center_lat, center_lon)
    return distance <= radius_km


def bearing_between_points(lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
    """
    Calculate initial bearing from point 1 to point 2.

    Args:
        lat1: Starting latitude in degrees
        lon1: Starting longitude in degrees
        lat2: Ending latitude in degrees
        lon2: Ending longitude in degrees

    Returns:
        Bearing in degrees (0-360)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))

    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)

    return (bearing_deg + 360) % 360
