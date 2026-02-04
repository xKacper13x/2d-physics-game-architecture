import pygame
import helpers
import math
import pymunk
import exceptions


class GameObject:
    """
    Podstawowa klasa dla wszystkich obiektów wizualnych w grze.

    Odpowiada za wczytanie grafiki, skalowanie oraz rysowanie obiektu
    na ekranie.

    Attributes:
        _name (str): Nazwa obiektu (np. do identyfikacji w debugowaniu).
         _img_path (str): Ścieżka do pliku graficznego.
        _image (pygame.Surface): Powierzchnia z załadowaną grafiką.
        _object_rect (pygame.Rect): Prostokąt otaczający obiekt.
        _pos (tuple | pygame.Vector2): Początkowa pozycja obiektu (x, y).
     """
    def __init__(self, object_data: dict,
                 position: tuple | pygame.Vector2 = None):
        """
        Inicjalizuje obiekt na podstawie słownika danych.

        Args:
            object_data (dict): Słownik zawierający klucze:
                - 'name': Nazwa obiektu.
                - 'img_path': Ścieżka do grafiki.
                - 'pos_x', 'pos_y': Współrzędne początkowe.
                - 'height' (opcjonalnie): Wysokość do skalowania.
                - 'width' (opcjonalnie): Szerokość do skalowania.
                - 'radius' (opcjonalnie): Promień (jeśli obiekt jest kołem).
        """
        self._name = object_data.get('name', '')
        self._img_path = object_data.get('img_path', '')

        if 'height' in object_data:
            self._height = int(object_data['height'])
            if 'width' in object_data:
                self._width = int(object_data.get('width', None))
                self._size = (self._width, self._height)
                self._image = self._load_image(self._img_path, self._size)
            else:
                self._image = self._load_image(self._img_path, self._height)
                self._width = self._image.get_width()
                self._size = (self._width, self._height)
        else:
            self._radius = int(object_data.get('radius', 0))
            diameter = int(2*self._radius)
            self._size = (diameter, diameter)
            try:
                helpers.check_size(self._size)
            except exceptions.InvalidConfigurationError:
                self._size = None

            self._image = self._load_image(self._img_path, self._size)

        self._object_rect = self._image.get_rect()
        if position is not None:
            self._pos = position
        else:
            self._pos = (object_data.get('pos_x', 0),
                         object_data.get('pos_y', 0))
        self._object_rect.center = self._pos

    @property
    def name(self) -> str:
        """Zwraca nazwę obiektu."""
        return self._name

    @property
    def position(self) -> pygame.Vector2:
        """Zwraca sktualną pozycję środka obiektu"""
        return pygame.Vector2(self._object_rect.center)

    def _load_image(self, img_path: str,
                    img_size: int | float | tuple |
                    pygame.Vector2 | None = None) -> None:
        """Helper do bezpiecznego ładowania obrazów."""
        return helpers.load_image(img_path, img_size)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Rysuje obiekt na ekranie w jego aktualnej pozycji.

        Args:
            screen (pygame.Surface): Ekran docelowy.
        """
        screen.blit(self._image, self._object_rect)

    def update(self, objects_to_kill: list = None):
        """Metoda do nadpisania w klasach pochodnych."""
        pass


class PhysicalObject(GameObject):
    """
    Klasa rozszerzająca GameObject o właściwości fizyczne (Pymunk).

    Obsługuje:
    - Masę, zdrowie i zadawanie obrażeń przy zderzeniach.
    - Synchronizację pozycji graficznej z ciałem fizycznym (Pymunk Body).
    - Rotację grafiki zgodnie z fizyką.
    - Zliczanie punktów za uszkodzenia.

    Attributes:
        _space (pymunk.Space): Przestrzeń fizyczna, do której należy obiekt.
        _mass (float): Masa obiektu.
        _health (float): Punkty życia (może być nieskończone 'inf').
        _score (int): Punkty zgromadzone za niszczenie tego obiektu.
        _body (pymunk.Body): Ciało fizyczne
        (musi być przypisane w klasie dziedziczącej).
        _last_angle (float): Kąt o jaki obiekt był obrócony
                             w poprzedniej klatce.
        _pos (tuple): Pozycja obiektu na ekranie.
    """
    def __init__(self, space: pymunk.Space, object_data: dict,
                 position: tuple | pygame.Vector2 = None):
        """
        Inicjalizuje obiekt fizyczny.

        Args:
            space (pymunk.Space): Przestrzeń symulacji.
            object_data (dict): Konfiguracja (masa, zdrowie, grafika).
        """
        self._space = space
        self._mass = object_data.get('mass', 1)
        self._mass = max(self._mass, 1)
        self._last_angle = 0.0

        super().__init__(object_data, position)

        self._health = object_data.get('health', 100)
        if self._health == 'inf':
            self._health = math.inf

        self._score = 0
        self._max_x = self._pos[0] + 100
        self._original_image = self._image

        self._last_velocity = pygame.Vector2(0, 0)

    @property
    def mass(self) -> int:
        """Zwraca masę obiektu."""
        return self._mass

    def collect_points(self) -> int:
        """
        Zwraca punkty zgromadzone przez obiekt (za obrażenia/zniszczenie)
        i resetuje licznik punktów.

        Returns:
            int: Liczba punktów do dodania do wyniku gracza.
        """
        points = self._score
        self._score = 0
        return points

    def _take_damage(self, damage: int) -> None:
        """
        Zadaje obrażenia obiektowi i nalicza punkty.

        Args:
            damage (float): Wartość obrażeń (siła uderzenia).
        """
        new_health = self._health - abs(damage)
        self._score += int(abs(damage) * 3)
        self._health = max(new_health, 0)

    def off_screen(self, screen_size: pygame.Vector2) -> bool:
        """
        Sprawdza, czy obiekt wyleciał daleko poza okno

        Args:
            screen_size (pygame.Vector2 | tuple): Wymiary ekranu.

        Returns:
            bool: True, jeśli obiekt jest daleko poza widokiem.
        """
        max_x = screen_size[0]
        off_screen = False
        if self._body.position.x > max_x + 150 or self._body.position.x < -150:
            off_screen = True

        return off_screen

    @property
    def velocity(self) -> pymunk.Vec2d:
        """Zwraca wektor prędkości ciała fizycznego."""
        return self._body.velocity

    def update(self, objects_to_kill: list | None = None) -> list | None:
        """
        Aktualizuje stan obiektu w każdej klatce.

        1. Synchronizuje pozycję grafiki z fizyką.
        2. Oblicza siłę uderzenia (zmiana prędkości).
        3. Zadaje obrażenia przy silnych kolizjach.
        4. Oznacza obiekt do usunięcia, jeśli zdrowie spadnie do 0.

        Args:
            objects_to_kill (list | None): Lista obiektów do usunięcia.

        Returns:
            list | None: Zaktualizowana lista obiektów do usunięcia.
        """
        pos_x = int(self._body.position.x)
        pos_y = int(self._body.position.y)
        self._object_rect.center = (pos_x, pos_y)
        if objects_to_kill is None:
            return None
        if self in objects_to_kill:
            return objects_to_kill

        current_velocity = self._body.velocity
        impact_velocity = current_velocity - self._last_velocity
        self._last_velocity = pygame.Vector2(current_velocity.x,
                                             current_velocity.y)

        impact_force = impact_velocity.length
        DAMAGE_THRESHOLD = 100

        if impact_force > DAMAGE_THRESHOLD:
            damage_to_deal = impact_force * 0.3
            self._take_damage(damage_to_deal)

        if self._body.position.x > self._max_x:
            self._health = 0
            self._score += 700

        if self._health <= 0:
            objects_to_kill.append(self)
        return objects_to_kill

    def draw(self, screen: pygame.Surface) -> None:
        """
        Rysuje obiekt z uwzględnieniem rotacji fizycznej.

        Args:
            screen (pygame.Surface): Ekran docelowy.
        """
        angle = self._body.angle
        angle = -1 * math.degrees(angle)

        # W celu optymalizacji gry, wykonuje transform,
        # tylko jeżeli obiekt się obrócił.
        if abs(angle - self._last_angle) > 1.0:
            self._image = pygame.transform.rotate(self._original_image, angle)
            self._last_angle = angle

        pos = self._body.position
        self._object_rect = self._image.get_rect(center=(pos.x, pos.y))

        super().draw(screen)
        self._max_x = screen.get_width()
