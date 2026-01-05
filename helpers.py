import os
import exceptions
import pygame


def check_path(path):
    if not os.path.exists(path):
        raise exceptions.MissingResourceError(path)


def check_size(size=0):
    if isinstance(size, int) or isinstance(size, float):
        if size <= 0:
            msg = f"Size must be greater than zero. Provided: {size}"
            raise exceptions.InvalidConfigurationError(msg)
    elif isinstance(size, pygame.Vector2) or isinstance(size, tuple):
        if size[0] <= 0 or size[1] <= 0:
            msg = (
                f"Both dimensions must be greater than zero. Provided: {size}")
            raise exceptions.InvalidConfigurationError(msg)
    else:
        msg = f"Unsupported type for size checking: {type(size)}"
        raise exceptions.InvalidConfigurationError(msg)


# None oznacza, że zostawiamy oryginalny rozmiar
def load_image(img_path, img_size=None):
    check_path(img_path)
    image = pygame.image.load(img_path).convert_alpha()

    if img_size is not None:
        check_size(img_size)
        # Podano tylko wysokość
        if isinstance(img_size, int):
            height = img_size
            ratio = image.get_width() / image.get_height()
            width = ratio * height
            final_img_size = (width, height)
        else:
            final_img_size = img_size
        image = pygame.transform.scale(image, final_img_size)
    return image


def initialize_font(font_path, font_size):
    check_path(font_path)
    check_size(font_size)
    if not pygame.font.get_init():
        pygame.font.init()
    font = pygame.font.Font(font_path, font_size)
    return font


def base_pos_on_anchor(anchor: str, size: pygame.Vector2) -> tuple:
    base_x, base_y = 0, 0
    size_w, size_h = size

    if anchor == 'center':
        base_x, base_y = size_w / 2, size_h / 2
    elif anchor == 'topleft':
        base_x, base_y = 0, 0
    elif anchor == 'topright':
        base_x, base_y = size_w, 0
    elif anchor == 'bottomleft':
        base_x, base_y = 0, size_h
    elif anchor == 'bottomright':
        base_x, base_y = size_w, size_h
    else:
        raise ValueError('Invalid anchor')

    return (base_x, base_y)
