import pygame
from entities import ui_elements


def test_text_creation_and_properties():
    """
    Verifies if Text instance is created properly
    """
    data = {
        'name': 'TestLabel',
        'text': 'Hello World',
        'font_size': 20,
        'text_color_R': 255,
        'text_color_G': 100,
        'text_color_B': 0,
        'anchor': 'center'
    }

    screen_rect = pygame.Rect(0, 0, 800, 600)

    text_obj = ui_elements.Text(data, screen_rect)

    assert text_obj.name == 'TestLabel'
    assert text_obj.text == 'Hello World'
    assert text_obj.text_color == (255, 100, 0)

    assert isinstance(text_obj._text_surface, pygame.Surface)
    assert text_obj._text_surface.get_width() > 0


def test_text_positioning():
    """Checks if text is centered on the screen"""
    data = {'text': 'X', 'anchor': 'center'}
    screen_rect = pygame.Rect(0, 0, 800, 600)

    text_obj = ui_elements.Text(data, screen_rect)

    assert int(text_obj._text_rect.centerx) == 400
    assert int(text_obj._text_rect.centery) == 300


def test_text_negative_font_size():
    """Checks if font_size is properly corrected"""
    data = {'text': 'X', 'anchor': 'center', 'font_size': -5}

    screen_rect = pygame.Rect(0, 0, 800, 600)
    text_obj = ui_elements.Text(data, screen_rect)

    assert text_obj.font_size == 1


def test_text_no_font_size():
    """Checks if font_size is set properly"""
    data = {'text': 'X', 'anchor': 'center'}

    screen_rect = pygame.Rect(0, 0, 800, 600)
    text_obj = ui_elements.Text(data, screen_rect)

    assert text_obj.font_size == 10


def test_text_invalid_color():
    """Checks if text_color is properly corrected"""
    data = {'text': 'X', 'anchor': 'center', 'text_color_R': 'black',
            'text_color_G': 300}

    screen_rect = pygame.Rect(0, 0, 800, 600)
    text_obj = ui_elements.Text(data, screen_rect)

    assert text_obj.text_color[0] == 0
    assert text_obj.text_color[1] == 255


# --- Button tests ---

def test_button_position_and_size():
    """
    Tests button creation.
    With no graphic file provided, helpers.load_image will return
    a pink placeholder.
    """
    data = {
        'img_path': 'non-existing-file.png',
        'width': 100,
        'height': 50,
        'anchor': 'topleft',
        'x_offset': 10,
        'y_offset': 10
    }
    screen_size = pygame.Vector2(800, 600)
    btn = ui_elements.Button(data, screen_size)

    assert btn.size == (100, 50)
    assert btn._object_rect.center == (10, 10)


# --- TextButton tests---

def test_text_button_structure():
    """Checks if TextButton creates Text instance properly."""
    data = {
        'img_path': 'dummy.png',
        'texts': [{'text': 'START', 'font_size': 15}],
        'anchor': 'center'
    }
    screen_size = pygame.Vector2(800, 600)

    txt_btn = ui_elements.TextButton(data, screen_size)

    assert isinstance(txt_btn._text, ui_elements.Text)
    assert txt_btn._text.text == 'START'
