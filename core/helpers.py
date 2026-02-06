import os
import exceptions
import pygame


def check_path(path: str | None) -> None:
    """
    Checks if the provided file path exists.

    Args:
        path (str | None): Path to the file or directory.

    Raises:
        exceptions.MissingResourceError: If the path is None
                                         or does not exist on disk.
    """
    if path is None:
        raise exceptions.MissingResourceError(path)
    if not os.path.exists(path):
        raise exceptions.MissingResourceError(path)


def check_size(size: int | float | tuple | pygame.Vector2 = 0) -> None:
    """
    Verifies if the provided size is valid (greater than zero).

    Args:
        size (int | float | tuple | pygame.Vector2): Size to validate.
            Can be a scalar or a pair of dimensions.

    Raises:
        exceptions.InvalidConfigurationError: If size is <= 0
                                        or the type is unsupported.
    """
    if size is None:
        msg = "No size provided."
        raise exceptions.InvalidConfigurationError(msg)
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


def validate_color(color_value: int) -> int:
    """
    Clamps an integer color component value between 0 and 255.

    Args:
        color_value (int): The color component value to validate.

    Returns:
        int: Validated value within the [0, 255] range.
    """
    if not isinstance(color_value, int):
        color_value = 0
    return max(0, min(255, color_value))


def load_image(img_path: str, img_size:
               (int | float | tuple | pygame.Vector2) = None
               ) -> pygame.Surface:
    """
    Safely loads an image from disk and optionally scales it.

    In case of an error (e.g., missing file, corrupt data), returns a
    pink placeholder surface to ensure the application continues running.

    Args:
        img_path (str): Path to the image file.
        img_size (int | float | tuple | pygame.Vector2 | None, optional):
            Target dimensions for scaling.
            - int/float: Proportional scaling based on height.
            - tuple/Vector2: Scaling to specific (width, height) dimensions.
            - None: Keeps the original image size.

    Returns:
        pygame.Surface: The loaded and scaled image,
                        or a placeholder on failure.
    """
    try:
        check_path(img_path)

        if pygame.display.get_surface() is None:
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

            if isinstance(img_size, (int, float)):
                height = image.get_height()
                if height != 0:
                    scale = image.get_width() / height
                    final_height = int(img_size)
                    final_width = int(final_height * scale)
                else:
                    final_width, final_height = int(img_size), int(img_size)

            else:
                final_width = int(img_size[0])
                final_height = int(img_size[1])

            image = pygame.transform.scale(image, (final_width, final_height))

        except (ValueError, TypeError, exceptions.InvalidConfigurationError):
            # Fallback: skip scaling if the provided size is invalid
            pass

    return image


def create_placeholder(
          size: int | float | tuple | pygame.Vector2 | None
          ) -> pygame.Surface:
    """
    Creates a 'Missing Texture' placeholder (bright magenta square).

    Args:
        size (int | float | tuple | pygame.Vector2 | None, optional):
            The desired size of the placeholder. Defaults to 50x50.

    Returns:
        pygame.Surface: A magenta surface representing a missing resource.
    """
    default_size = 50
    w, h = default_size, default_size

    try:
        if size is not None:
            if isinstance(size, (int, float)):
                val = int(size)
                if val > 0:
                    w, h = val, val

            elif isinstance(size, (tuple, list, pygame.Vector2)):
                if len(size) >= 2:
                    safe_w = int(size[0])
                    safe_h = int(size[1])
                    if safe_w > 0 and safe_h > 0:
                        w, h = safe_w, safe_h

    except (ValueError, TypeError, AttributeError):
        pass

    w = max(1, w)
    h = max(1, h)

    surface = pygame.Surface((w, h))
    surface.fill((255, 0, 255))
    return surface


def initialize_font(font_path: str | None,
                    font_size: int | float) -> pygame.font.Font:
    """
    Initializes a Pygame font object.

    If the provided path is invalid or missing, it falls back to the
    default system font.

    Args:
        font_path (str | None): Path to the .ttf/.otf file or None for default.
        font_size (int | float): Desired font size.

    Returns:
        pygame.font.Font: A font object ready for text rendering.
    """
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
    """
    Calculates anchor point coordinates based on a container size.

    Used for UI positioning. If an invalid anchor name is provided,
    the function defaults to the center of the container.

    Args:
        anchor (str): Anchor name ('topleft', 'topright', 'bottomleft',
                      'bottomright', or 'center').
        size (pygame.Vector2 | tuple): Dimensions of the container.

    Returns:
        tuple: (x, y) coordinates of the anchor point.
    """
    base_x, base_y = 0, 0

    try:
        check_size(size)
        size = pygame.Vector2(size)
    except (exceptions.InvalidConfigurationError, ValueError, TypeError):
        size = (1920, 1080)
    size_w, size_h = size

    if anchor == 'topleft':
        base_x, base_y = 0, 0
    elif anchor == 'topright':
        base_x, base_y = size_w, 0
    elif anchor == 'bottomleft':
        base_x, base_y = 0, size_h
    elif anchor == 'bottomright':
        base_x, base_y = size_w, size_h
    else:
        base_x, base_y = size_w / 2, size_h / 2

    return (base_x, base_y)
