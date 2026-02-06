from entities.objects_base import PhysicalObject
import pymunk


class Structure(PhysicalObject):
    """
    Klasa reprezentująca element konstrukcyjny (blok, skrzynka, belka).

    Są to obiekty fizyczne, które tworzą budowle chroniące przeciwników.
    Mogą zostać zniszczone przez uderzenie, posiadają masę i tarcie.
    Dziedziczy rysowanie po klasie PhysicalObject.
    """
    def __init__(self, space: pymunk.Space, object_data: dict):
        """
        Inicjalizuje strukturę.

        Args:
            space (pymunk.Space): Przestrzeń fizyczna symulacji.
            object_data (dict): Słownik konfiguracyjny.
        """
        super().__init__(space, object_data)
        self._mass = object_data['mass']

        self._img_path = object_data['img_path']
        self._create_physics(space)

    def _create_physics(self, space: pymunk.Space) -> None:
        """
        Tworzy ciało fizyczne i kształt bloku w Pymunk.

        Ustawia:
        - Moment bezwładności dla prostokąta.
        - Hitbox zgodny z wymiarami grafiki.
        - Wysokie tarcie (żeby konstrukcje się nie rozjeżdżały).

        Args:
            space (pymunk.Space): Przestrzeń symulacji.
        """
        # oblicza moment bezwladności
        self._moment = pymunk.moment_for_box(self._mass, self._size)
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.DYNAMIC)
        self._body.position = self._pos
        self._shape = pymunk.Poly.create_box(self._body, self._size)

        self._shape.friction = 0.5
        self._shape.elasticity = 0.1
        self._shape.game_object = self

        space.add(self._body, self._shape)

    def update(self, screen_size: tuple,
               objects_to_kill: list | None = None) -> list | None:
        """
        Aktualizuje stan struktury.

        Wywołuje bazową logikę fizyczną (obrażenia od uderzeń, niszczenie).

        Args:
            objects_to_kill (list | None): Lista obiektów do usunięcia.

        Returns:
            list | None: Zaktualizowana lista obiektów do usunięcia.
        """
        if objects_to_kill is None:
            return []
        return super().update(screen_size, objects_to_kill)

    def draw(self, screen):
        super().draw(screen)
