from menu_states import State
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


def test_initialize_font_invalid_path():
    state = State((1920, 1080))
    with pytest.raises(exceptions.MissingResourceError):
        state.initialize_font('path', 10)


def test_initialize_font_invalid_size():
    state = State((1920, 1080))
    with pytest.raises(exceptions.InvalidConfigurationError):
        state.initialize_font('assets/fonts/angrybirds-regular.ttf', 0)
