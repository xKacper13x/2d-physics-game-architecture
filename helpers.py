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
    """
    Bezpiecznie ładuje obrazek.
    W razie błędu zwraca różowy kwadrat (placeholder).
    """
    try:
        check_path(img_path)
        # .convert_alpha() może rzucić błąd, jeśli ekran nie jest zainicjowany
        if pygame.display.get_surface() is None:
            # Bez konwersji, jeśli brak ekranu
            image = pygame.image.load(img_path)
        else:
            image = pygame.image.load(img_path).convert_alpha()

    except (exceptions.MissingResourceError, pygame.error, FileNotFoundError):
        return create_placeholder(img_size)

    if img_size is not None:
        try:
            check_size(img_size)
            final_width = 0
            final_height = 0

            # Skalowanie proporcjonalne (podana tylko wysokość jako int)
            if isinstance(img_size, (int, float)):
                height = image.get_height()
                if height != 0:
                    scale = image.get_width() / height
                    final_height = int(img_size)
                    final_width = int(final_height * scale)
                else:
                    final_width, final_height = int(img_size), int(img_size)

            # Skalowanie do konkretnych wymiarów (tuple/Vector2)
            else:
                final_width = int(img_size[0])
                final_height = int(img_size[1])

            image = pygame.transform.scale(image, (final_width, final_height))

        except (ValueError, TypeError, exceptions.InvalidConfigurationError):
            # Zwróci obraz w oryginalnym rozmiarze
            pass

    return image


def create_placeholder(size):
    """
    Pomocnicza funkcja tworząca 'Missing Texture' (różowy kwadrat)
    """
    default_size = 50
    w, h = default_size, default_size

    try:
        if size is not None:
            if isinstance(size, (int, float)):
                val = int(size)
                if val > 0:
                    w, h = val, val

            # 2. Jeśli podano krotkę/wektor (szer, wys)
            elif isinstance(size, (tuple, list, pygame.Vector2)):
                if len(size) >= 2:
                    safe_w = int(size[0])
                    safe_h = int(size[1])
                    if safe_w > 0 and safe_h > 0:
                        w, h = safe_w, safe_h

    except (ValueError, TypeError, AttributeError):
        # Jeśli cokolwiek pójdzie nie tak przy odczycie rozmiaru,
        # ignorujemy to i zostajemy przy 50x50.
        pass

    # Pilnuje żeby nie stworzyć powierzchni 0x0
    w = max(1, w)
    h = max(1, h)

    surface = pygame.Surface((w, h))
    surface.fill((255, 0, 255))
    return surface


def initialize_font(font_path, font_size):
    try:
        check_size(font_size)
        size = int(font_size)
    except (exceptions.InvalidConfigurationError, ValueError, TypeError):
        size = 35

    if not pygame.font.get_init():
        pygame.font.init()
    try:
        check_path(font_path)
        font = pygame.font.Font(font_path, size)
    except (exceptions.MissingResourceError, pygame.error):
        font = pygame.font.Font(None, size)
    return font


def base_pos_on_anchor(anchor: str, size: pygame.Vector2 | tuple) -> tuple:
    base_x, base_y = 0, 0

    try:
        check_size(size)
        size = pygame.Vector2(size)
    except (exceptions.InvalidConfigurationError, ValueError, TypeError):
        size = (1920, 1080)
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
