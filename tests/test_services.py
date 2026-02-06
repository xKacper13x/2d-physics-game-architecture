import json
from services.level_service import LevelService
from services.trajectory_service import TrajectoryService
import pathlib
import pytest
import pygame


def test_level_service_physics_config(tmp_path):
    """Verifies that gravity data is correctly parsed from JSON."""
    d = tmp_path / "configs"
    d.mkdir()
    config_file = d / "level1.json"
    config_file.write_text(json.dumps({
        "gravity_x": 10,
        "gravity_y": -500,
        "high_score": 1000
    }))

    service = LevelService(config_dir=str(d))
    service.load_data("level1.json")

    assert service.physics_config == (10, -500)
    assert isinstance(service.physics_config, tuple)


def test_level_service_physics_config_default(tmp_path):
    """
    Validates fallback values when gravity keys
    are missing in the configuration.
    """
    d = tmp_path / "configs"
    d.mkdir()
    config_file = d / "level1.json"
    config_file.write_text(json.dumps({
        "high_score": 1000
    }))

    service = LevelService(config_dir=str(d))
    service.load_data("level1.json")

    assert service.physics_config == (0, -900)
    assert isinstance(service.physics_config, tuple)


def test_save_new_high_score_logic(tmp_path):
    """
    Tests the logic for updating the level's record.
    """
    d = tmp_path / "configs"
    d.mkdir()
    config_file = d / "level1.json"
    config_file.write_text(json.dumps({"high_score": 500}))

    service = LevelService(config_dir=str(d))
    service.load_data("level1.json")

    assert service.save_new_high_score(1, 300) is False
    assert service.save_new_high_score(1, 700) is True


def test_double_file_name_given(tmp_path):
    """
    Checks if load_data() handles user giving file's name twice.
    Should run without exceptions.
    """
    d = tmp_path / "configs"
    d.mkdir()
    config_file = d / "level1.json"
    config_file.write_text(json.dumps({"high_score": 500}))

    path = pathlib.Path(d) / 'level1.json'
    service = LevelService(path)
    data = service.load_data(path)
    assert data['high_score'] == 500


def test_invalid_path(tmp_path):
    """
    Exercises defensive programming triggers.

    Confirms that ValueError and FileNotFoundError are raised
    for incorrect extensions or missing files.
    """
    d = tmp_path / "configs"
    d.mkdir()
    service = LevelService(config_dir=str(d))

    with pytest.raises(ValueError):
        service.load_data("level1.txt")

    with pytest.raises(FileNotFoundError):
        service.load_data("level.json")


def test_load_corrupted_json(tmp_path):
    """
    Validates the parsing layer's resilience.

    Ensures that json.JSONDecodeError is correctly surfaced
    when encountering malformed data.
    """
    d = tmp_path / "configs"
    d.mkdir()

    corrupted_file = d / 'level1.json'
    corrupted_file.write_text('kkkk')

    service = LevelService(corrupted_file)
    with pytest.raises(json.JSONDecodeError):
        service.load_data(corrupted_file)


class MockPhysicsParams:
    def __init__(self, mass, gravity, power, direction):
        self.mass = mass
        self.gravity = gravity
        self.power = power
        self.direction = direction


class MockWorldBounds:
    def __init__(self, screen_center, ground_level):
        self.screen_center = screen_center
        self.ground_level = ground_level


@pytest.fixture
def basic_setup():
    """This fixture prepares standart test data."""
    start_pos = pygame.Vector2(100, 500)
    physics = MockPhysicsParams(
        mass=1.0,
        gravity=pygame.Vector2(0, 900),
        power=100.0,
        direction=pygame.Vector2(1, -1).normalize()
    )
    bounds = MockWorldBounds(
        screen_center=1000,
        ground_level=800
    )
    return start_pos, physics, bounds


def test_trajectory_returns_points(basic_setup):
    """Verifies that this service return a list of points"""
    start_pos, physics, bounds = basic_setup

    points = TrajectoryService.get_trajectory_points(start_pos, physics,
                                                     bounds)

    assert isinstance(points, list)
    assert len(points) > 0

    assert isinstance(points[0], tuple)
    assert isinstance(points[0][1], pygame.Vector2)


def test_physics_zero_gravity(basic_setup):
    """
    Checks if trajectory is a straight line when gravity equals 0.
    """
    start_pos, physics, bounds = basic_setup
    physics.gravity = pygame.Vector2(0, 0)

    points = TrajectoryService.get_trajectory_points(start_pos, physics,
                                                     bounds)

    p1 = points[0][1]
    p2 = points[1][1]
    p3 = points[2][1]

    diff1 = p2 - p1
    diff2 = p3 - p2

    assert diff1.x == pytest.approx(diff2.x, rel=1e-5)
    assert diff1.y == pytest.approx(diff2.y, rel=1e-5)


def test_negative_gravity(basic_setup):
    """
    Checks if the object goes up while gracity is set to negative number.
    """
    start_pos, physics, bounds = basic_setup
    physics.gravity = pygame.Vector2(0, -900)

    points = TrajectoryService.get_trajectory_points(start_pos, physics,
                                                     bounds)

    last_point = points[-1][1]
    assert last_point.y < start_pos.y


def test_trajectory_stops_at_ground(basic_setup):
    """Checks edge case: loop must break when we hit the ground."""
    start_pos, physics, bounds = basic_setup

    points = TrajectoryService.get_trajectory_points(start_pos, physics,
                                                     bounds)

    last_point = points[-1][1]

    assert last_point.y > start_pos.y  # Should be lower than starting pos
    assert last_point.y <= bounds.ground_level + 100  # Safety margin


def test_trajectory_stops_at_screen_center(basic_setup):
    """Checks edge case: loop breaks after crossing middle of the screen"""
    start_pos, physics, bounds = basic_setup
    bounds.screen_center = 200
    bounds.ground_level = 100000

    points = TrajectoryService.get_trajectory_points(start_pos, physics,
                                                     bounds)
    last_point = points[-1][1]

    assert last_point.x <= bounds.screen_center + 20  # safety margin


def test_mass_impact():
    """Tests if mass changes influence trajectory."""
    start_pos = pygame.Vector2(0, 0)
    gravity = pygame.Vector2(0, 10)
    direction = pygame.Vector2(1, -1).normalize()
    bounds = MockWorldBounds(1000, 1000)

    # Light object
    light_physics = MockPhysicsParams(mass=1.0, gravity=gravity, power=100,
                                      direction=direction)
    light_points = TrajectoryService.get_trajectory_points(start_pos,
                                                           light_physics,
                                                           bounds)

    # Heavy object (same force, higher mass -> smaller velocity)
    heavy_physics = MockPhysicsParams(mass=100.0, gravity=gravity, power=100,
                                      direction=direction)
    heavy_points = TrajectoryService.get_trajectory_points(start_pos,
                                                           heavy_physics,
                                                           bounds)

    # Light object should go further after time travel time
    assert light_points[5][1].x > heavy_points[5][1].x
