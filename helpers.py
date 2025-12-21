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
        image = pygame.transform.scale(image, img_size)
    return image


def initialize_font(font_path, font_size):
    check_path(font_path)
    check_size(font_size)
    if not pygame.font.get_init():
        pygame.font.init()
    font = pygame.font.Font(font_path, font_size)
    return font
