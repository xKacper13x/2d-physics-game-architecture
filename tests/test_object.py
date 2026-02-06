import pytest
import pygame
import pymunk
from unittest.mock import patch
from entities.objects_base import PhysicalObject


# --- FIXTURES  ---

@pytest.fixture
def mock_image_loader():
    """
    This fixture makes helpers.load_image return ready surface
    in order to make tests faster and easier to conduct.
    """
    with patch('core.helpers.load_image') as mock_load:
        mock_load.return_value = pygame.Surface((10, 10))
        yield mock_load


@pytest.fixture
def basic_object(mock_image_loader):
    """
    Creates an instance of PhysicalObject with easy to test data.

    Returns:
        PhysicalObject: A safe-to-test object instance with default data.
    """
    space = pymunk.Space()
    object_data = {
        'name': 'test_obj',
        'img_path': 'doesnt matter',
        'mass': 3,
        'height': 1.5,
        'pos_x': 500,
        'pos_y': 400
    }

    obj = PhysicalObject(space, object_data)
    obj._body = pymunk.Body(1, 1)
    obj._body.velocity = (0, 0)
    obj._last_velocity = pygame.Vector2(0, 0)
    return obj


# --- Unit tests ---

def test_mass_validation_negative(mock_image_loader):
    """Checks if objects corrects its mass while negative."""
    space = pymunk.Space()
    obj_data = {
                'mass': -100
               }
    obj = PhysicalObject(space, obj_data, (0, 0))

    assert obj.mass == 1


def test_take_damage_and_scoring(basic_object):
    """Checks taking damage and counting points"""
    initial_health = basic_object._health
    damage = 20

    basic_object._take_damage(damage)

    assert basic_object._health == initial_health - damage

    assert basic_object.collect_points() == damage * 3

    assert basic_object.collect_points() == 0


def test_death_logic(basic_object):
    """
    Verifies that the object is marked for removal upon fatal damage.
    (Damage equal to health in order to check the edge case)
    """
    damage = basic_object._health
    screen_size = (100, 100)
    basic_object._take_damage(damage)

    obj_to_kill = []
    basic_object.update(screen_size, obj_to_kill)
    assert basic_object in obj_to_kill


def test_off_screen(basic_object):
    """
    Verifies that the off_screen() method correctly identifies
    objects within and outside the screen boundaries.
    """
    screen_size = (400, 500)

    basic_object._body.position = (200, 200)
    assert basic_object.off_screen(screen_size) is False

    basic_object._body.position = (1000, 250)
    assert basic_object.off_screen(screen_size) is True


def test_death_off_screen(basic_object):
    """
    Verifies that object dies while being off screen.
    """
    basic_object._body.position = (-1000, 250)
    screen_size = (100, 100)

    obj_to_kill = []
    basic_object.update(screen_size, obj_to_kill)
    assert basic_object in obj_to_kill
    assert basic_object.collect_points() == 700
