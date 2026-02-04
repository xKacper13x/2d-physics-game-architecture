from .base_state import State
from entities.objects_base import PhysicalObject
from entities.static_objects import Slingshot, Ground
from entities.enemy import Enemy
from entities.projectile import Projectile
from entities.structure import Structure
from services.level_service import LevelService
from core.signals import GameSignal
from services.trajectory_service import TrajectoryService
from core.physics_data import PhysicsParams, WorldBounds
from core.input_handler import InputData
import pygame
import pymunk


class GameState(State):
    """
    Stan gry reprezentujący poziomy gry.

    Klasa ta odpowiada za:
    - Zarządzanie obiektami fizycznymi, tworzenie, aktualizowanie,
      rysowanie i niszczenie ich.
    - Inicjalizowanie przestrzeni do obliczeń fizycznych.
    - Określenie działania i zasad gry.
    - Zarządzanie wejściem pobranym od użytkownika.

    Attributes:
        _ammo_pointer (int): Wskaźnik na aktualnie używany pocisk.
        _level (int): Numer poziomu gry.
        _space (pymunk.Space): Przestrzeń fizyczna symulacji.
        _high_score (int): Zapisany w pliku konfiguracyjnym gry, rekord
                           punktowy poziomu.

        _current_score (int): Aktualnie uzyskany wynik punktowy.
        _max_dis (int): Maksymalne możliwe naciągnięcie procy.
        _projectile_stopped (bool): Flaga określająca, czy wystrzelony pocisk
                                    przestał się poruszać.
        _level_ended (bool): Flaga określająca, czy aktualny poziom
                             zakończył się.
        _timer (float): Stoper mierzący opóźnienie zakończenia poziomu i
                        przejścia do kolejnego stanu
        _wait_time (int): ustalone opóźnienie przejścia do kolejnego stanu.
        _ground (Ground): Obiekt statycznego podłoża.
        _enemies (list): Lista przeciwników.
        _object_on_sling (Projectile): Pocisk aktualnie znajdujący się na
                                       procy.
        _dragged_object (Projectile): Pocisk aktualnie trzymany przez kursor.
        _structures (list): Lista struktur.
        _slingshot (Slingshot): Obiekt procy.
    """
    def __init__(self, screen_size: pygame.Vector2, level: int):
        """
        Inicjalizuje stan gry dla podanego poziomu.

        Args:
            screen_size (pygame.Vector2): Rozmiar okna gry.
            level (int): Numer poziomu do załadowania.

        Raises:
            ValueError: Jeśli numer poziomu nie jest liczbą całkowitą.
        """
        if not isinstance(level, int):
            raise ValueError('Level must be an integer')
        self._ammo_pointer = 0
        self._level = level
        self._space = pymunk.Space()

        self._trajectory_service = TrajectoryService()
        self._level_service = LevelService('objects_config_files')
        data = self._level_service.load_data(f'level{level}.json')
        self._space.gravity = self._level_service.physics_config
        self._high_score = self._level_service.high_score

        super().__init__(screen_size, data)
        background_img_path = data["background_img"]
        self._set_background(background_img_path)
        self._create_buttons()

        self._current_score = 0
        self._update_score_labels(self._current_score, self._high_score)

        self._max_dis = int(self._slingshot.height * 0.8)
        self._object_on_sling = self._current_projectile
        self._dragged_object = None

        self._projectile_stopped = False
        self._level_ended = False
        self._timer = 0
        self._wait_time = 2

        self._ground = Ground(self._screen_size, 940, self._space)

    @property
    def level(self) -> int:
        """
        Zwraca numer aktualnego poziomu.

        Returns:
            int: Numer poziomu.
        """
        return self._level

    @property
    def current_score(self) -> int:
        """
        Zwraca aktualny wynik gracza.

        Returns:
            int: Liczba punktów.
        """
        return self._current_score

    @property
    def high_score(self) -> int:
        """
        Zwraca najlepszy wynik (rekord) dla tego poziomu.

        Returns:
            int: Rekord punktowy.
        """
        return self._high_score

    @property
    def scores(self) -> tuple:
        """
        Zwraca krotkę z wynikami (bieżący, rekord).

        Returns:
            tuple: (current_score, high_score).
        """
        return (self._current_score, self._high_score)

    def _create_buttons(self) -> None:
        """
        Przypisuje przycisk do zmiennej
        """
        self._pause_button = self._buttons_dict['pause_button']

    def _initialize_objects(self, data: dict) -> list:
        """
        Inicjalizuje obiekty gry (proca, wrogowie, struktury) podanych danych.

        Args:
            data (dict): Słownik konfiguracyjny.

        Returns:
            list: Lista wszystkich obiektów do aktualizowania i rysowania.
        """
        objects = super()._initialize_objects(data)
        data = data['objects']

        self._slingshot = Slingshot(data)
        pos = self._slingshot.position
        self._slingshot_pos = (pos[0], pos[1] - 95)

        self._projectiles_data = data['projectiles']
        self._current_projectile = self._initialize_projectile()
        objects.append(self._current_projectile)

        self._enemies = [Enemy(self._space, enemy_data)
                         for enemy_data in data['enemies']]
        self._structures = [Structure(self._space, structure_data)
                            for structure_data in data['structures']]
        return objects + self._enemies + self._structures

    def _initialize_projectile(self) -> Projectile:
        """
        Tworzy nowy obiekt pocisku na podstawie danych konfiguracyjnych.

        Returns:
            Projectile: Nowy obiekt pocisku.
        """
        data = self._projectiles_data[self._ammo_pointer]
        projectile = Projectile(self._space, data, self._slingshot_pos)
        return projectile

    def _perform_launch(self) -> None:
        """
        Oblicza wektor siły i wystrzeliwuje pocisk z procy.
        """
        start_pos = self._current_projectile.position
        pull_vector = self._slingshot_pos - start_pos

        distance = pull_vector.length()
        MIN_DIS = 70

        if distance >= MIN_DIS:
            power = self._slingshot.power
            self._current_projectile.launch((pull_vector.x*power,
                                             pull_vector.y*power))
        else:
            self._current_projectile.go_to_start_pos()

    def _check_for_launch(self, lmb_released: bool, lmb_pressed: bool,
                          mouse_pos: tuple) -> None:
        """
        Obsługuje logikę myszy (chwytanie, ciągnięcie, puszczanie procy).

        Args:
            events (list): Lista zdarzeń Pygame.
        """
        # obsluga puszczenia myszy(strzal lub reset)
        if lmb_released:
            if self._dragged_object is not None:
                self._perform_launch()
                self._dragged_object = None

        is_ammo_dragged = self._current_projectile.is_dragged(lmb_pressed,
                                                              mouse_pos)
        if is_ammo_dragged or self._dragged_object is not None:
            self._dragged_object = self._current_projectile
            self._dragged_object.drag(self._slingshot_pos,
                                      mouse_pos,
                                      self._max_dis)
        # Zabezpieczenie: jeśli nie trzymamy przycisku, puszczamy obiekt
        elif lmb_pressed:
            self._dragged_object = None

    def _kill_object(self, obj_to_remove: PhysicalObject) -> None:
        """
        Usuwa obiekt fizyczny z gry i symulacji.

        Args:
            obj (PhysicalObject): Obiekt do usunięcia.
        """
        space_bodies = self._space.bodies
        if obj_to_remove._body in space_bodies:
            self._space.remove(obj_to_remove._body, obj_to_remove._shape)
        if obj_to_remove in self._objects:
            self._objects.remove(obj_to_remove)
        if isinstance(obj_to_remove, Enemy):
            self._enemies.remove(obj_to_remove)

    def _end_level(self) -> None:
        """
        Rozpoczyna zakończenie poziomu. Zaznacza poziom jako zakończony
        i resetuje wynik w przypadku porażki.
        """
        if self._enemies:
            self._current_score = 0
        self._timer = 0
        self._level_ended = True

    def _draw_trajectory(self, screen: pygame.Surface):
        """
        Rysuje celownik(przewidywaną trajektorię lotu pocisku).

        Args:
            screen (pygame.Surface): ekran docelowy
        """
        if self._dragged_object is None:
            return

        sling_pos = pygame.Vector2(self._slingshot_pos)
        start_pos = pygame.Vector2(self._current_projectile.position)
        diff = sling_pos - start_pos
        power = self._slingshot.power

        mass = self._current_projectile.mass
        gravity = pygame.Vector2(self._space.gravity)

        x_middle = self._screen_size[0] / 2
        ground_y = self._ground.pos_y

        physics_params = PhysicsParams(mass, gravity, power, diff)
        world_bounds = WorldBounds(ground_y, x_middle)
        points = self._trajectory_service.get_trajectory_points(start_pos,
                                                                physics_params,
                                                                world_bounds)

        for index, point in points:
            radius = 5 - (index // 10)
            radius = max(radius, 2)
            pygame.draw.circle(screen, (255, 255, 255), point, radius)
            pygame.draw.circle(screen, (0, 0, 0), point, radius, 1)

    def _draw_objects(self, screen: pygame.Surface):
        """
        Rysuje obiekty gry z uwzględnieniem warstw procy (przód/tył).

        Args:
            screen (pygame.Surface): ekran docelowy
        """
        if self._object_on_sling is not None:
            rubber_anchor = self._object_on_sling.rubber_anchor
            self._slingshot.draw_inner_rubber(screen,
                                              rubber_anchor)
            super()._draw_objects(screen)
            self._slingshot.draw_outer_rubber(screen,
                                              rubber_anchor)
        else:
            self._slingshot.draw_outer_rubber(screen)
            super()._draw_objects(screen)

    def _update_entities(self) -> None:
        """Aktualizuje obiekty, zlicza punkty i usuwa zniszczone."""
        objects_to_kill = []
        for obj in self._objects:
            if isinstance(obj, (Enemy, Structure)):
                objects_to_kill = obj.update(objects_to_kill)
                self._current_score += obj.collect_points()
                self._update_score_labels(self._current_score,
                                          self._high_score)
            else:
                obj.update()

        for obj in objects_to_kill:
            self._kill_object(obj)

    def _update_slingshot_status(self, mouse_pos: tuple) -> None:
        """Sprawdza, czy pocisk znajduje się na procy."""
        if self._current_projectile.is_on_sling(self._max_dis):
            self._object_on_sling = self._current_projectile
        else:
            self._object_on_sling = None

    def _update_projectile_status(self, mouse_pos: tuple) -> None:
        """
        Zarządza cyklem życia pocisku po wystrzale.
        Wykrywa zatrzymanie lub wylot poza ekran i przygotowuje kolejny strzał.
        """
        if self._current_projectile.is_on_sling(self._max_dis):
            return

        if not self._projectile_stopped:
            velocity = pygame.Vector2(
                            self._current_projectile.velocity).length()

            is_stopped = velocity < 4
            is_off_screen = self._current_projectile.off_screen(
                                                            self._screen_size)

            if is_stopped or is_off_screen:
                self._projectile_stopped = True

                # Reset timera dla opoźnienia zakończenia poziomu
                self._timer = 0

    def _handle_input(self, lmb_clicked: bool, mouse_pos: tuple,
                      key_esc_down: bool) -> str:
        """
        Sprawdza kliknięcie przycisku pauzy lub klawisza ESC.

        Args:
            events (list): Lista zdarzeń Pygame.

        Returns:
            str: Komenda sterująca, informująca o następnym stanie.
        """
        result = GameSignal.STAY
        if self._pause_button.is_clicked(lmb_clicked, mouse_pos):
            result = GameSignal.PAUSE_GAME

        if key_esc_down:
            result = GameSignal.PAUSE_GAME
        return result

    def update(self, input_data: InputData) -> str:
        """
        Główna metoda aktualizacji poziomu gry.
        - Krok fizyki
        - Sprawdzenie i obsługa strzału.
        - Aktualizacja statusu procy.
        - Aktualizacja wrogów i struktur.
        - Zarządzanie pociskami.
        - Obsługa zmiany pocisku.
        - Obsługa UI
        - Sprawdzenie warunków końca poziomu.

        Args:
            events (list): lista zdarzeń Pygame.

        Returns:
            str: Komenda sterująca, informująca o następnym stanie.
        """
        self._space.step(1/60)

        if not self._level_ended:
            self._check_for_launch(input_data.lmb_released,
                                   input_data.lmb_pressed,
                                   input_data.mouse_pos)

        self._update_slingshot_status(input_data.mouse_pos)

        self._update_entities()

        self._update_projectile_status(input_data.mouse_pos)
        # Gdy wszystkie obiekty przeciwników zostały zniszczone
        # i odliczanie do zakończenia poziomu nie zostało jeszcze uruchomione,
        # rozpoczyna zakończenie poziomu
        if not self._enemies and not self._level_ended:
            self._end_level()

        if self._projectile_stopped:
            self._timer += 1/60
            if self._timer >= 2:
                self._ammo_pointer += 1
                self._kill_object(self._current_projectile)

                if self._ammo_pointer >= len(self._projectiles_data):
                    if not self._level_ended:
                        self._end_level()
                else:
                    self._current_projectile = self._initialize_projectile()
                    self._objects.append(self._current_projectile)
                    self._projectile_stopped = False
                    self._timer = 0

        next_state = self._handle_input(input_data.lmb_clicked,
                                        input_data.mouse_pos,
                                        input_data.key_esc_down)

        if self._level_ended:
            self._timer += 1/60  # Dodajemy czas jednej klatki
            if self._timer >= self._wait_time:
                self._level_service.save_new_high_score(self._level,
                                                        self._current_score)
                next_state = GameSignal.END_LEVEL
        return next_state

    def draw(self, screen: pygame. Surface) -> None:
        """
        Rysuje cały stan gry.

        Args:
            screen (pygame.Surface): ekran docelowy
        """
        super().draw(screen)
        self._draw_trajectory(screen)
        self._slingshot.draw(screen)
