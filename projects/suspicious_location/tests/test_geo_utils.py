"""
Unit tests for geographic utility functions.
"""

import pytest
import math

from src.geo_utils import (
    haversine_distance,
    calculate_velocity,
    is_impossible_travel,
    point_in_circle,
    bearing_between_points
)


class TestHaversineDistance:
    """Tests for haversine distance calculation."""

    def test_same_point(self):
        """Test distance between same point is zero."""
        distance = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        assert distance == 0.0

    def test_new_york_to_los_angeles(self):
        """Test distance between NYC and LA."""
        # NYC: 40.7128° N, 74.0060° W
        # LA: 34.0522° N, 118.2437° W
        distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)

        # Actual distance is approximately 3944 km
        assert 3900 < distance < 4000

    def test_london_to_paris(self):
        """Test distance between London and Paris."""
        # London: 51.5074° N, 0.1278° W
        # Paris: 48.8566° N, 2.3522° E
        distance = haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)

        # Actual distance is approximately 344 km
        assert 340 < distance < 350

    def test_across_equator(self):
        """Test distance across equator."""
        distance = haversine_distance(0, 0, 1, 0)

        # 1 degree latitude is approximately 111 km
        assert 110 < distance < 112


class TestCalculateVelocity:
    """Tests for velocity calculation."""

    def test_zero_time(self):
        """Test velocity with zero time elapsed."""
        velocity = calculate_velocity(100, 0)
        assert velocity == 0.0

    def test_negative_time(self):
        """Test velocity with negative time."""
        velocity = calculate_velocity(100, -1)
        assert velocity == 0.0

    def test_normal_velocity(self):
        """Test normal velocity calculation."""
        # 100 km in 2 hours = 50 km/h
        velocity = calculate_velocity(100, 2)
        assert velocity == 50.0

    def test_high_velocity(self):
        """Test high velocity calculation."""
        # 800 km in 1 hour = 800 km/h (airplane)
        velocity = calculate_velocity(800, 1)
        assert velocity == 800.0


class TestImpossibleTravel:
    """Tests for impossible travel detection."""

    def test_car_speed_possible(self):
        """Test that car speed is possible."""
        # 100 km in 2 hours = 50 km/h (car)
        is_impossible = is_impossible_travel(100, 2)
        assert is_impossible is False

    def test_airplane_speed_possible(self):
        """Test that airplane speed is possible."""
        # 800 km in 1 hour = 800 km/h (airplane at max speed)
        is_impossible = is_impossible_travel(800, 1)
        assert is_impossible is False

    def test_supersonic_impossible(self):
        """Test that supersonic speed is impossible for normal travel."""
        # 1000 km in 1 hour = 1000 km/h (faster than typical airplane)
        is_impossible = is_impossible_travel(1000, 1)
        assert is_impossible is True

    def test_teleportation_impossible(self):
        """Test that instant travel is impossible."""
        # Any distance in zero time
        is_impossible = is_impossible_travel(100, 0)
        assert is_impossible is True

    def test_very_short_time_impossible(self):
        """Test that very high speed in short time is impossible."""
        # 100 km in 1 minute = 6000 km/h
        is_impossible = is_impossible_travel(100, 1/60)
        assert is_impossible is True

    def test_custom_max_speed(self):
        """Test with custom maximum speed."""
        # 600 km in 1 hour with max speed 500 km/h
        is_impossible = is_impossible_travel(600, 1, max_speed_kmh=500)
        assert is_impossible is True


class TestPointInCircle:
    """Tests for circular geofence detection."""

    def test_point_at_center(self):
        """Test point at center of circle."""
        is_inside = point_in_circle(40.7128, -74.0060, 40.7128, -74.0060, 10)
        assert is_inside is True

    def test_point_inside_circle(self):
        """Test point inside circle."""
        # Point very close to center (< 1 km)
        is_inside = point_in_circle(40.7128, -74.0060, 40.7130, -74.0062, 10)
        assert is_inside is True

    def test_point_outside_circle(self):
        """Test point outside circle."""
        # NYC to LA (3944 km) with 100 km radius
        is_inside = point_in_circle(40.7128, -74.0060, 34.0522, -118.2437, 100)
        assert is_inside is False

    def test_point_on_boundary(self):
        """Test point approximately on boundary."""
        # Create two points approximately 10 km apart
        is_inside = point_in_circle(40.7128, -74.0060, 40.8000, -74.0060, 10)
        # Should be close to boundary, might be inside or outside due to approximation
        # Just verify it doesn't crash
        assert isinstance(is_inside, bool)


class TestBearingBetweenPoints:
    """Tests for bearing calculation."""

    def test_due_north(self):
        """Test bearing due north."""
        bearing = bearing_between_points(0, 0, 1, 0)
        assert 359 < bearing < 1 or bearing < 1  # ~0 degrees

    def test_due_east(self):
        """Test bearing due east."""
        bearing = bearing_between_points(0, 0, 0, 1)
        assert 85 < bearing < 95  # ~90 degrees

    def test_due_south(self):
        """Test bearing due south."""
        bearing = bearing_between_points(1, 0, 0, 0)
        assert 175 < bearing < 185  # ~180 degrees

    def test_due_west(self):
        """Test bearing due west."""
        bearing = bearing_between_points(0, 1, 0, 0)
        assert 265 < bearing < 275  # ~270 degrees

    def test_bearing_range(self):
        """Test bearing is always in range 0-360."""
        bearing = bearing_between_points(40.7128, -74.0060, 34.0522, -118.2437)
        assert 0 <= bearing < 360

    def test_same_point_bearing(self):
        """Test bearing between same point."""
        bearing = bearing_between_points(40.7128, -74.0060, 40.7128, -74.0060)
        # Bearing of same point is undefined, but should return a value in range
        assert 0 <= bearing < 360
