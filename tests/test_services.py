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
    """Przygotowuje standardowe dane testowe (Fixtures)."""
    start_pos = pygame.Vector2(100, 500) # Startujemy z lewej strony
    physics = MockPhysicsParams(
        mass=1.0,
        gravity=pygame.Vector2(0, 900), # Grawitacja w dół
        power=100.0,
        direction=pygame.Vector2(1, -1).normalize() # Strzał w górę i w prawo
    )
    bounds = MockWorldBounds(
        screen_center=1000,
        ground_level=800
    )
    return start_pos, physics, bounds


def test_trajectory_returns_points(basic_setup):
    """Sprawdza, czy serwis w ogóle zwraca listę punktów."""
    start_pos, physics, bounds = basic_setup

    points = TrajectoryService.get_trajectory_points(start_pos, physics, bounds)

    assert isinstance(points, list)
    assert len(points) > 0
    # Sprawdź strukturę: (index, Vector2)
    assert isinstance(points[0], tuple)
    assert isinstance(points[0][1], pygame.Vector2)


def test_physics_zero_gravity(basic_setup):
    """
    Test fizyczny: Jeśli nie ma grawitacji, ruch powinien być liniowy.
    To jest test, który sprawdza poprawność wzoru s = s0 + vt.
    """
    start_pos, physics, bounds = basic_setup
    physics.gravity = pygame.Vector2(0, 0) # Wyłączamy grawitację

    points = TrajectoryService.get_trajectory_points(start_pos, physics, bounds)

    # Pobieramy dwa punkty
    p1 = points[0][1]
    p2 = points[1][1]
    p3 = points[2][1]

    # Obliczamy wektory przesunięcia
    diff1 = p2 - p1
    diff2 = p3 - p2

    # W ruchu jednostajnym (bez grawitacji) przesunięcia powinny być identyczne
    # Używamy pytest.approx, bo liczby zmiennoprzecinkowe mogą się różnić o 0.000001
    assert diff1.x == pytest.approx(diff2.x, rel=1e-5)
    assert diff1.y == pytest.approx(diff2.y, rel=1e-5)


def test_trajectory_stops_at_ground(basic_setup):
    """Sprawdza warunek brzegowy: pętla musi się przerwać, gdy uderzymy w ziemię."""
    start_pos, physics, bounds = basic_setup

    points = TrajectoryService.get_trajectory_points(start_pos, physics, bounds)

    last_point = points[-1][1]

    # Ostatni punkt powinien być blisko ziemi lub tuż pod nią
    # Logika pętli to: while curr_pos.y <= ground_y
    # Więc ostatni wygenerowany punkt MOŻE minimalnie przekroczyć granicę
    # Ale nie powinien lecieć w nieskończoność.

    assert last_point.y > start_pos.y # Powinien spaść niżej niż start

    # Sprawdzamy czy ostatni punkt jest w "rozsądnej" okolicy granicy
    # (nie powinien być np. 2000 pikseli pod ziemią przy małym kroku czasowym)
    assert last_point.y >= bounds.ground_level - 100  # Margines bezpieczeństwa


def test_trajectory_stops_at_screen_center(basic_setup):
    """Sprawdza warunek brzegowy: pętla przerywa się po przekroczeniu środka ekranu."""
    start_pos, physics, bounds = basic_setup
    bounds.screen_center = 200
    bounds.ground_level = 100000

    points = TrajectoryService.get_trajectory_points(start_pos, physics,
                                                     bounds)
    last_point = points[-1][1]

    # Punkt powinien przekroczyć lub dotrzeć do screen_center
    assert last_point.x >= 200


def test_mass_impact():
    """Testuje, czy zmiana masy wpływa na trajektorię (F=ma => a=F/m)."""
    start_pos = pygame.Vector2(0, 0)
    gravity = pygame.Vector2(0, 10)
    direction = pygame.Vector2(1, -1).normalize()
    bounds = MockWorldBounds(1000, 1000)

    # Lekki obiekt
    light_physics = MockPhysicsParams(mass=1.0, gravity=gravity, power=100, direction=direction)
    light_points = TrajectoryService.get_trajectory_points(start_pos, light_physics, bounds)

    # Ciężki obiekt (ta sama siła, większa masa -> mniejsza prędkość)
    heavy_physics = MockPhysicsParams(mass=100.0, gravity=gravity, power=100, direction=direction)
    heavy_points = TrajectoryService.get_trajectory_points(start_pos, heavy_physics, bounds)

    # Lekki obiekt powinien polecieć dalej/szybciej w tym samym czasie
    assert light_points[5][1].x > heavy_points[5][1].x
