import pytest
import pygame
import core.helpers as helpers
import exceptions


# --- Unit tests for check_size ---

def test_check_size_correct():
    """Checks if functions accepts correct data."""
    helpers.check_size(100)
    helpers.check_size((800, 600))
    helpers.check_size(pygame.Vector2(50, 50))
    # No exception == succes


def test_check_size_errors():
    """Verifies that function raises exceptions for invalid data"""
    # Zero
    with pytest.raises(exceptions.InvalidConfigurationError):
        helpers.check_size(0)

    # Negatice
    with pytest.raises(exceptions.InvalidConfigurationError):
        helpers.check_size(-10)

    # Tuple containing zero
    with pytest.raises(exceptions.InvalidConfigurationError):
        helpers.check_size((100, 0))


# --- Unit tests for check_path ---

def test_check_path_existing_file(tmp_path):
    """
    Verifies that function accepts correct data
    """
    real_file = tmp_path / "test_file.txt"
    real_file.write_text("hello")

    path_str = str(real_file)

    helpers.check_path(path_str)


def test_check_path_missing_file():
    """Checks reaction for non-existing file"""
    with pytest.raises(exceptions.MissingResourceError):
        helpers.check_path("this_file_does_not_exist.png")


def test_check_path_none():
    """Checks reaction for None."""
    with pytest.raises(exceptions.MissingResourceError):
        helpers.check_path(None)


# --- Tests for placeholder ---

def test_create_placeholder_returns_surface():
    """Verifies that function returns pygame.Surface."""
    result = helpers.create_placeholder((30, 40))

    assert isinstance(result, pygame.Surface)
    assert result.get_width() == 30
    assert result.get_height() == 40

    color = result.get_at((0, 0))
    assert color == (255, 0, 255, 255)


# --- Tests for base_pos_on_anchor ---

def test_base_pos_calculation():
    """Checks positions"""
    screen = (800, 600)

    # Middle
    assert helpers.base_pos_on_anchor('center', screen) == (400, 300)

    # top-right corner
    assert helpers.base_pos_on_anchor('topright', screen) == (800, 0)


def test_load_image_missing_file_returns_placeholder():
    """
    Verifies that loading a non-existing file will cause the function
    to return a pink square instead.
    """
    result = helpers.load_image("non_existing_file.png", img_size=(20, 20))

    assert isinstance(result, pygame.Surface)
    assert result.get_size() == (20, 20)
    assert result.get_at((0, 0)) == (255, 0, 255, 255)
