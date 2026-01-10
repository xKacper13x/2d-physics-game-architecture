from entities.objects_base import PhysicalObject
import pymunk


class Enemy(PhysicalObject):
    """
    Klasa reprezentująca przeciwnika w grze.

    Dziedziczy po PhysicalObject, więc posiada fizykę, zdrowie i grafikę.
    Dodatkowo implementuje logikę natychmiastowej śmierci przy kontakcie
    z pociskiem gracza.

    Attributes:
        _pos (int): Pozycja obiektu.
        _moment (float): Moment bezwładności ciała.
        _body (pymunk.Body): Ciało fizyczne obiektu.
        _shape (pymunk.shapes.Poly): Hitbox obiektu.
        _health (int): Zdrowie obiektu.
        _score (int): wynik nabity na obiekcie.
    """
    def __init__(self, space, object_data):
        """
        Inicjalizuje przeciwnika.

        Args:
            space (pymunk.Space): Przestrzeń fizyczna symulacji.
            object_data (dict): Słownik konfiguracyjny.
        """
        super().__init__(space, object_data)

        self._create_physics(space)

    def _create_physics(self, space: pymunk.Space) -> None:
        """
        Tworzy ciało fizyczne i kształt przeciwnika w bibliotece Pymunk.

        Ustawia:
        - Moment bezwładności (dla pudełka).
        - Ciało dynamiczne.
        - Kształt (prostokąt, nieco węższy niż grafika
            dla lepszego dopasowania).
        - Fizykę (tarcie, sprężystość).
        - Referencję zwrotną (shape.game_object) dla detekcji kolizji.

        Args:
            space (pymunk.Space): Przestrzeń symulacji.
        """
        self._moment = pymunk.moment_for_box(self._mass, self._size)
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.DYNAMIC)
        self._body.position = self._pos
        self._shape = pymunk.Poly.create_box(self._body, (self._width * 0.8,
                                                          self._height))
        self._shape.friction = 0.5
        self._shape.elasticity = 0.1
        space.add(self._body, self._shape)

    def update(self, objects_to_kill: list | None = None) -> list | None:
        """
        Aktualizuje stan przeciwnika.

        Sprawdza kolizje z pociskami (natychmiastowa śmierć) oraz
        wywołuje bazową aktualizację fizyczną (obrażenia od uderzeń).

        Args:
            objects_to_kill (list | None): Lista obiektów do usunięcia.

        Returns:
            list | None: Zaktualizowana lista obiektów do usunięcia.

        Raises:
            ValueError: Jeśli nie przekazano listy objects_to_kill.
        """
        if objects_to_kill is None:
            raise ValueError('update() method requires objects_to_kill_list')

        contacts = self._space.shape_query(self._shape)
        for contact in contacts:
            other_shape = contact.shape
            if hasattr(other_shape, 'game_object'):
                who_hit_me = other_shape.game_object

                if type(who_hit_me).__name__ == 'Projectile':
                    self._health = 0
                    self._score += 1000

        return super().update(objects_to_kill)
