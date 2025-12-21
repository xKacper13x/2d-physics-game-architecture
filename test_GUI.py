from menu_states import State
from buttons import Button
import exceptions
import pytest
import pygame
import os


def test_load_image_no_size():
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((1, 1))

    state = State((1920, 1080))
    img = state.load_image('assets/images/Title_Screen.jpg')
    assert img.get_width() == 1920
    assert img.get_height() == 1080


def test_load_image_invalid_path():
    state = State((1920, 1080))
    with pytest.raises(exceptions.MissingResourceError):
        state.load_image('random_img')


def test_button_pos():
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((1, 1))

    button = Button((0, 0), (5, 5), 'assets/images/Title_Screen.jpg')
    assert button.position() == (0, 0)


def test_button_size():
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((1, 1))

    button = Button((0, 0), (5, 5), 'assets/images/Title_Screen.jpg')
    assert button.size() == (5, 5)


def test_button_invalid_size_x():
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((1, 1))

    with pytest.raises(exceptions.InvalidConfigurationError):
        Button((0, 0), (-1, 5), 'assets/images/Title_Screen.jpg')


def test_button_invalid_size_y():
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((1, 1))

    with pytest.raises(exceptions.InvalidConfigurationError):
        Button((0, 0), (5, -1), 'assets/images/Title_Screen.jpg')
