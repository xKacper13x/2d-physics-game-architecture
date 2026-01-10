from entities.objects_base import PhysicalObject
import pygame
import pymunk


class Projectile(PhysicalObject):
    """
    Klasa reprezentująca pocisk (ptaka) wystrzeliwanego z procy.

    Obsługuje:
    - Przeciąganie myszką (naciąganie procy).
    - Fizykę lotu (po wystrzeleniu).
    - Wykrywanie momentu opuszczenia procy (dla animacji gumy).
    - Obliczanie punktu zaczepienia gumy.

    Attributes:
        _pull_vector (pygame.Vector2): Wektor naciągu (kierunek,
                                       z którego strzelamy).
                                       Używany do sprawdzania,
                                       kiedy pocisk minie procę.
        _start_pos (tuple): Pozycja początkowa (środek procy),
                            do której pocisk wraca przy anulowaniu.
        _shape (pymunk.Poly): Hitbox obiektu.
    """
    def __init__(self, space: pymunk.Space,
                 object_data: dict, position: tuple):
        """
        Inicjalizuje pocisk.

        Args:
            space (pymunk.Space): Przestrzeń fizyczna.
            object_data (dict): Słownik konfiguracyjny (masa, grafika itp.).
            slingshot_pos (tuple): Pozycja środka procy
                                   (punkt startowy pocisku).
        """
        self._mass = object_data['mass']

        self._pos = position
        super().__init__(space, object_data)
        self._score = object_data['score']
        self._pull_vector = pygame.Vector2(0, 0)

        self._create_physics(space)

    def _create_physics(self, space: pymunk.Space) -> None:
        """
        Tworzy ciało fizyczne pocisku.

        Początkowo ciało jest STATYCZNE (nie spada),
        aby można je było naciągać.
        Zmienia się na DYNAMICZNE dopiero w momencie strzału.

        Args:
            space (pymunk.Space): Przestrzeń fizyczna.
        """
        # oblicza moment bezwladności
        self._moment = 999990
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.STATIC)
        self._body.position = self._pos
        self._shape = pymunk.Circle(self._body, self._radius)

        self._shape.friction = 1.0
        self._shape.elasticity = 0.7
        self._shape.game_object = self

        space.add(self._body, self._shape)

    def launch(self, impulse_vector: tuple) -> None:
        """
        Wystrzeliwuje pocisk.

        Zmienia typ ciała na DYNAMICZNY i przykłada impuls siły.
        Zapamiętuje wektor naciągu, aby wiedzieć, w którą stronę leci.

        Args:
            impulse_vector (tuple): Wektor siły (x, y) impulsu.
        """
        self._body.body_type = pymunk.Body.DYNAMIC
        self._body.mass = self._mass
        self._body.moment = self._moment

        self._body.apply_impulse_at_local_point(impulse_vector)
        start_vec = pygame.math.Vector2(self._pos)
        current_vec = pygame.math.Vector2(self.position())

        self._pull_vector = current_vec - start_vec

    def go_to_start_pos(self) -> None:
        """Resetuje pozycję pocisku do środka procy (anulowanie strzału)."""
        self._body.position = self._pos

    def is_dragged(self) -> bool:
        """
        Sprawdza, czy gracz chwycił pocisk myszką.

        Returns:
            bool: True, jeśli LPM jest wciśnięty, kursor jest na pocisku,
                  a pocisk jest w stanie statycznym (na procy).
        """
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            m_collision = self._object_rect.collidepoint(mouse_pos)
            if m_collision and self._body.body_type == pymunk.Body.STATIC:
                return True
        return False

    def is_on_sling(self, slingshot_pos: tuple, max_distance: int) -> bool:
        """
        Sprawdza, czy pocisk nadal fizycznie znajduje się na gumie procy.

        Logika opiera się na iloczynie skalarnym: dopóki pocisk znajduje się
        "za procą" (po stronie naciągu), uznajemy, że jest na gumie.
        Gdy minie środek procy w locie, guma znika.

        Args:
            slingshot_pos (tuple): Pozycja procy.
            max_distance (int): Maksymalna długość naciągu.

        Returns:
            bool: True, jeśli pocisk jest na gumie.
        """
        if self._body.body_type != pymunk.Body.DYNAMIC:
            return True

        slingshot_center = pygame.math.Vector2(self._pos)
        current_pos = pygame.math.Vector2(self.position())
        current_vector = current_pos - slingshot_center

        # 3. ILOCZYN SKALARNY (Dot Product)
        # Sprawdzamy kąt między "Wektorem Naciągu" a "Aktualnym Wektorem".
        # Jeśli wynik > 0:
        # Pocisk jest nadal po stronie naciągu (Leci do procy).
        # Jeśli wynik < 0:
        # Pocisk minął środek procy i leci w świat (Guma znika).
        dot_product = current_vector.dot(self._pull_vector)
        vector = self._get_mouse_vector(slingshot_pos)
        if dot_product > 0 and vector.length() <= max_distance:
            return True
        else:
            return False

    def _get_mouse_vector(self, slingshot_pos: tuple) -> pygame.Vector2:
        """
        Oblicza wektor od procy do kursora myszy.

        Args:
            slingshot_pos (tuple): Pozycja procy.

        Returns:
            pygame.Vector2: Wektor wskazujący na mysz.
        """
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        sling_x = slingshot_pos[0]
        sling_y = slingshot_pos[1]

        vector = pygame.Vector2(mouse_x - sling_x, mouse_y - sling_y)
        return vector

    def drag(self, slingshot_pos: tuple, max_distance: int) -> None:
        """
        Aktualizuje pozycję pocisku podczas przeciągania myszką.

        Ogranicza odległość naciągu do `max_distance` (clamp).

        Args:
            slingshot_pos (tuple): Środek procy.
            max_distance (int): Maksymalny zasięg naciągu.
        """
        vector = self._get_mouse_vector(slingshot_pos)
        if vector.length() > max_distance:
            vector.scale_to_length(max_distance)

        new_pos = pygame.Vector2(slingshot_pos) + vector
        self._body.position = tuple(new_pos)

    def body(self) -> pymunk.Body:
        """Zwraca ciało fizyczne."""
        return self._body

    def shape(self):
        """Zwraca hitbox obiektu."""
        return self._shape

    def get_rubber_anchor(self) -> tuple:
        """
        Oblicza punkt na krawędzi pocisku, do którego ma być przyczepiona guma.
        Znajdujący się po przeciwnej stronie pocisku względem procy.

        Returns:
            tuple: Współrzędne (x, y) punktu zaczepienia.
        """
        projectile_center = pygame.math.Vector2(self.position())
        slingshot_center = pygame.math.Vector2(self._pos)

        direction = slingshot_center - projectile_center

        # Zabezpieczenie: jeśli ptak jest idealnie w środku procy (długość 0),
        # zwracamy lewą stronę
        if direction.length() == 0:
            return self._object_rect.midleft

        # Normalizacja: Skracamy wektor do długości 1, zachowując kierunek
        direction = direction.normalize()

        # Mnożymy przez promień ptaka
        # Dzięki temu wektor sięga od środka idealnie do krawędzi
        anchor_vector = projectile_center - (direction * self._radius)

        return (anchor_vector.x, anchor_vector.y)
