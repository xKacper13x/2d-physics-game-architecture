from entities.objects_base import GameObject
import pymunk
import pygame


class Slingshot(GameObject):
    """
    Klasa reprezentująca procę (wyrzutnię).

    Odpowiada za:
    - Wyświetlanie grafiki procy.
    - Rysowanie gumy (cięciwy).
    - Przechowywanie informacji o sile naciągu.

    Attributes:
        _power (int): Mnożnik siły wyrzutu.
        _rubber_color (tuple): Kolor gumy (R, G, B).
        _rubber_width (int): Grubość rysowanej linii gumy.
        _left_fork_offset (pygame.Vector2): Przesunięcie lewych widełek
                                            względem środka procy.
        _right_fork_offset (pygame.Vector2): Przesunięcie prawych widełek
                                             względem środka procy.
    """
    def __init__(self, data: dict):
        """
        Inicjalizuje procę.

        Args:
            data (dict): Główny słownik konfiguracyjny poziomu.
                         Musi zawierać klucz 'slingshot' z parametrami procy.
        """
        object_data = data['slingshot']
        self._pos = (object_data['pos_x'], object_data['pos_y'])
        super().__init__(object_data)
        self._power = object_data['power']

        self._rubber_color = (object_data['color_R'], object_data['color_G'],
                              object_data['color_B'])
        self._rubber_width = object_data['rubber_width']

        self._left_fork_offset = pygame.math.Vector2(self._width / -4.15,
                                                     self._height / -3)
        self._right_fork_offset = pygame.math.Vector2(self._width / 4.15,
                                                      self._height / -2.6)

    def get_power(self) -> int:
        """Zwraca mnożnik siły procy."""
        return self._power

    def get_height(self) -> int:
        """Zwraca wysokość grafiki procy (używane do limitowania naciągu)."""
        return self._height

    def draw_outer_rubber(self, screen: pygame.Surface,
                          projectile_pos: tuple | None = None) -> None:
        """
        Rysuje tylną część gumy (tę, która powinna być ZA pociskiem).

        Jeśli proca jest w spoczynku (projectile_pos is None),
        rysuje prostą linię między widełkami.

        Args:
            screen (pygame.Surface): Ekran docelowy.
            projectile_pos (tuple | None): Pozycja naciągniętego pocisku.
        """
        left_fork = self._pos + self._left_fork_offset
        if projectile_pos is None:
            right_fork = self._pos + self._right_fork_offset
            pygame.draw.line(screen, self._rubber_color, left_fork,
                             right_fork, self._rubber_width)
        else:
            pygame.draw.line(screen, self._rubber_color, left_fork,
                             projectile_pos, self._rubber_width)

    def draw_inner_rubber(self, screen: pygame.Surface,
                          projectile_pos: tuple) -> None:
        """
        Rysuje przednią część gumy (tę, która powinna być PRZED pociskiem).

        Args:
            screen (pygame.Surface): Ekran docelowy.
            projectile_pos (tuple): Pozycja naciągniętego pocisku.
        """
        right_fork = self._pos + self._right_fork_offset
        pygame.draw.line(screen, self._rubber_color, right_fork,
                         projectile_pos, self._rubber_width)


class Ground:
    """
    Klasa reprezentująca fizyczne podłoże (ziemię).

    Jest to obiekt niewidoczny, ale posiadający
    fizyczne właściwości (kolizje), które zapobiegają spadaniu obiektów
    w nieskończoność.

    Attributes:
        _y_pos (int): Pozycja Y poziomu ziemi.
        _body (pymunk.Body): Statyczne ciało fizyczne.
        _shape (pymunk.Segment): Kształt (linia) reprezentujący ziemię.
    """
    def __init__(self, screen_size: pygame.Vector2, y_pos: int,
                 space: pymunk.Space):
        """
        Inicjalizuje fizykę ziemi.

        Args:
            screen_size (pygame.Vector2): Rozmiar okna (do obliczenia
                                                        szerokości ziemi).
            y_pos (int): Współrzędna Y, na której znajduje się podłoga.
            space (pymunk.Space): Przestrzeń symulacji.
        """
        self._width = 3 * screen_size[0]
        self._y_pos = y_pos

        self._start_point = (-350, self._y_pos)
        self._end_point = (self._width, self._y_pos)
        self._create_physics(space)

    def get_pos_y(self) -> int:
        """Zwraca poziom Y podłogi."""
        return self._y_pos

    def _create_physics(self, space: pymunk.Space) -> None:
        """
        Tworzy statyczny segment (linię) w Pymunk.

        Segment posiada wysokie tarcie (żeby obiekty się nie ślizgały)
        i niską sprężystość (żeby się nie odbijały jak od trampoliny).
        """
        self._body = space.static_body

        self._shape = pymunk.Segment(self._body, self._start_point,
                                     self._end_point, 5)

        # Właściwości fizyczne
        # Maksymalne tarcie (żeby elementy się nie ślizgały jak na lodzie)
        self._shape.friction = 1.0

        # Mała sprężystość (żeby nie odbijały się jak od trampoliny)
        self._shape.elasticity = 0.2

        space.add(self._shape)
