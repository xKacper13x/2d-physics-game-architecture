import os
import exceptions
import pygame


def check_path(path: str | None) -> None:
    """
    Sprawdza, czy podana ścieżka do pliku istnieje.

    Args:
        path (str): Ścieżka do pliku lub katalogu.

    Raises:
        exceptions.MissingResourceError: Jeśli ścieżka nie istnieje.
    """
    if path is None:
        raise exceptions.MissingResourceError(path)
    if not os.path.exists(path):
        raise exceptions.MissingResourceError(path)


def check_size(size: int | float | tuple | pygame.Vector2 = 0) -> None:
    """
    Weryfikuje, czy podany rozmiar jest poprawny (większy od zera).

    Args:
        size (int | float | tuple | pygame.Vector2): Rozmiar do sprawdzenia.
                                                     Może być liczbą
                                                     lub parą liczb.

    Raises:
        exceptions.InvalidConfigurationError: Jeśli rozmiar jest <= 0
                                              lub typ jest nieobsługiwany.
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


# None oznacza, że zostawiamy oryginalny rozmiar
def load_image(img_path: str, img_size:
               (int | float | tuple | pygame.Vector2) = None
               ) -> pygame.Surface:
    """
    Bezpiecznie ładuje obrazek z dysku i opcjonalnie go skaluje.

    W przypadku błędu (brak pliku, uszkodzony plik) zwraca różowy kwadrat
    (placeholder), aby gra mogła kontynuować działanie.

    Args:
        img_path (str): Ścieżka do pliku graficznego.
        img_size (int | float | tuple | pygame.Vector2 | None, optional):
            Docelowy rozmiar.
            - Jeśli int/float: Skaluje proporcjonalnie wg wysokości.
            - Jeśli tuple/Vector2: Skaluje do konkretnych wymiarów (szer, wys).
            - Jeśli None: Zostawia oryginalny rozmiar.

    Returns:
        pygame.Surface: Załadowany i przeskalowany obraz lub placeholder.
    """
    try:
        check_path(img_path)

        # Ładowanie obrazka
        if pygame.display.get_surface() is None:
            image = pygame.image.load(img_path)
        else:
            image = pygame.image.load(img_path).convert_alpha()

    except (exceptions.MissingResourceError, pygame.error, FileNotFoundError):
        return create_placeholder(img_size)

    # LOGIKA SKALOWANIA - Wykonujemy tylko jeśli podano rozmiar
    if img_size is not None:
        try:
            check_size(img_size)

            final_width = 0
            final_height = 0

            # Skalowanie proporcjonalne (podana tylko wysokość jako int/float)
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
            # W razie błędnego rozmiaru, zwracamy oryginał (lub placeholder)
            # Tutaj decydujemy się po prostu pominąć skalowanie
            pass

    return image


def create_placeholder(
          size: int | float | tuple | pygame.Vector2 | None
          ) -> pygame.Surface:
    """
    Tworzy 'Missing Texture' (jaskrawy różowy kwadrat) o zadanym rozmiarze.

    Args:
        size (int | float | tuple | pygame.Vector2 | None, optional):
            Oczekiwany rozmiar placeholdera.

    Returns:
        pygame.Surface: Różowa powierzchnia (Magenta).
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


def initialize_font(font_path: str | None,
                    font_size: int | float) -> pygame.font.Font:
    """
    Inicjalizuje czcionkę Pygame.

    Jeśli podana ścieżka jest nieprawidłowa,
    ładuje domyślną czcionkę systemową.

    Args:
        font_path (str | None): Ścieżka do pliku .ttf/.otf lub
                                None dla domyślnej.
        font_size (int | float): Rozmiar czcionki.

    Returns:
        pygame.font.Font: Obiekt czcionki gotowy do renderowania tekstu.
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
    Oblicza współrzędne punktu zakotwiczenia (anchor) dla
    danego rozmiaru ekranu/obiektu. W przypadku podania
    niepoprawnego anchor, ustawia środek ekranu/obiektu.

    Args:
        anchor (str): Nazwa zakotwiczenia ('center', 'topleft', 'topright',
                      'bottomleft', 'bottomright').
        size (pygame.Vector2 | tuple): Wymiary kontenera (np. ekranu).
                                       Domyślnie fallbackuje do (1920, 1080)
                                       w razie błędu.

    Returns:
        tuple: Współrzędne (x, y) punktu zakotwiczenia.
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
        # domyślnie ustawiamy center
        base_x, base_y = size_w / 2, size_h / 2

    return (base_x, base_y)
