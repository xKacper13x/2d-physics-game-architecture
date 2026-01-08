from .base_state import State
from entities.objects_base import PhysicalObject
from entities.static_objects import Slingshot, Ground
from entities.enemy import Enemy
from entities.projectile import Projectile
from entities.structure import Structure
import pygame
import pymunk
import json
import helpers


class GameState(State):
    def __init__(self, screen_size, level: int):
        if not isinstance(level, int):
            raise ValueError('Level must be an integer')
        self._ammo_pointer = 0
        self._level = level
        self._space = pymunk.Space()

        path = f'objects_config_files/level{self._level}.json'
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._space.gravity = (data['gravity_x'], data['gravity_y'])
            self._high_score = data['high_score']
            background_img_path = data["background_img"]
            self._set_background(background_img_path)
            self._create_buttons()

        self._current_score = 0
        self._update_score_labels(self._current_score, self._high_score)

        self._max_dis = self._slingshot.get_height() * 0.8

        self._object_on_sling = self._current_projectile
        self._dragged_object = None

        self._projectile_stopped = False
        self._level_ended = False
        self._timer = 0
        self._wait_time = 2.0

        self._ground = Ground(self._screen_size, 920, self._space)

    def get_level(self):
        return self._level

    def get_scores(self) -> tuple:
        scores = (self._current_score, self._high_score)
        return scores

    def _create_buttons(self):
        self._pause_button = self._buttons_dict['pause_button']

    def _initialize_objects(self, data):
        objects = super()._initialize_objects(data)
        data = data['objects']

        self._slingshot = Slingshot(data)
        pos = self._slingshot.position()
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
        data = self._projectiles_data[self._ammo_pointer]
        projectile = Projectile(self._space, data, self._slingshot_pos)
        return projectile

    def _handle_mouse_release(self, events):
        """Sprawdza, czy gracz puścił mysz, aby wystrzelić pocisk."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self._dragged_object is not None:
                    self._perform_launch()
                self._dragged_object = None

    def _perform_launch(self):
        """Wydzielona logika obliczania wektora strzału."""
        start_pos = self._current_projectile.position()
        pull_vector = self._slingshot_pos - start_pos

        distance = pull_vector.length()
        MIN_DIS = 70

        if distance >= MIN_DIS:
            power = self._slingshot.get_power()
            self._current_projectile.launch((pull_vector.x*power,
                                             pull_vector.y*power))
        else:
            self._current_projectile.go_to_start_pos()

    def _check_for_launch(self, events):
        # obsluga puszczenia myszy(strzal lub reset)
        self._handle_mouse_release(events)

        is_ammo_dragged = self._current_projectile.is_dragged()
        if is_ammo_dragged or self._dragged_object is not None:
            self._dragged_object = self._current_projectile
            self._dragged_object.drag(self._slingshot_pos, self._max_dis)
        elif not pygame.mouse.get_pressed()[0]:
            self._dragged_object = None

    def _draw_objects(self, screen):
        if self._object_on_sling is not None:
            rubber_anchor = self._object_on_sling.get_rubber_anchor()
            self._slingshot.draw_inner_rubber(screen,
                                              rubber_anchor)
            super()._draw_objects(screen)
            self._slingshot.draw_outer_rubber(screen,
                                              rubber_anchor)
        else:
            self._slingshot.draw_outer_rubber(screen)
            super()._draw_objects(screen)

    def _kill_object(self, obj_to_remove: PhysicalObject) -> None:
        space_bodies = self._space.bodies
        if obj_to_remove._body in space_bodies:
            self._space.remove(obj_to_remove._body, obj_to_remove._shape)
        if obj_to_remove in self._objects:
            self._objects.remove(obj_to_remove)
        if isinstance(obj_to_remove, Enemy):
            self._enemies.remove(obj_to_remove)

    def _end_level(self):
        if self._enemies:
            self._current_score = 0
        self._timer = 0
        self._level_ended = True

    def save_high_score(self):
        path = f'objects_config_files/level{self._level}.json'
        if self._current_score > self._high_score:
            self._high_score = self._current_score

        helpers.check_path(path)
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
        data['high_score'] = max(self._current_score, self._high_score)

        with open(path, 'w') as file_handle:
            json.dump(data, file_handle, indent=4)

    def _draw_trajectory(self, screen):
        if self._dragged_object is None:
            return

        start_pos = pygame.Vector2(self._current_projectile.position())
        diff = self._slingshot_pos - start_pos
        power = self._slingshot.get_power()
        impulse = diff * power

        mass = self._current_projectile.get_mass()
        # Unika dzielenia przez0
        mass = max(1, mass)
        velocity = impulse / mass

        # Symulacja trajektorii
        gravity = pygame.Vector2(self._space.gravity)
        curr_pos = start_pos
        time_step = 0.12
        i = 1

        x_middle = self._screen_size[0] / 2
        ground_y = self._ground.get_pos_y()
        while curr_pos.y <= ground_y and curr_pos.x <= x_middle:
            t = i * time_step + time_step
            i += 1

            # Wzór na pozycję: s = s0 + vt + 0.5at^2
            curr_pos = start_pos + (velocity * t) + (0.5 * gravity * t * t)

            # Rysowanie kropki
            radius = 5 - (i // 10)
            radius = max(radius, 2)

            pygame.draw.circle(screen, (255, 255, 255), curr_pos, radius)
            pygame.draw.circle(screen, (0, 0, 0), curr_pos, radius, 1)

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

    def _update_slingshot_status(self):
        if self._current_projectile.is_on_sling(self._slingshot_pos,
                                                self._max_dis):
            self._object_on_sling = self._current_projectile
        else:
            self._object_on_sling = None

    def _update_projectile_status(self):
        """
        Sprawdza, czy wystrzelony pocisk się zatrzymał
        lub wyleciał poza ekran.
        """
        if self._current_projectile.is_on_sling(self._slingshot_pos,
                                                self._max_dis):
            return

        if not self._projectile_stopped:
            velocity = pygame.Vector2(
                            self._current_projectile.velocity()).length()

            is_stopped = velocity < 4
            is_off_screen = self._current_projectile.off_screen(
                                                            self._screen_size)

            if is_stopped or is_off_screen:
                self._projectile_stopped = True

                # Reset timera dla opoźnienia zakończenia poziomu
                self._timer = 0

    def _handle_input(self, events):
        result = self
        if self._pause_button.is_clicked(events):
            result = 'PAUSE_GAME'

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                result = PauseState(self._screen_size, self)
        return result

    def update(self, events: list) -> State:
        self._space.step(1/60)

        if not self._level_ended:
            self._check_for_launch(events)

        self._update_slingshot_status()

        self._update_entities()

        self._update_projectile_status()
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

        next_state = self._handle_input(events)

        if self._level_ended:
            self._timer += 1/60  # Dodajemy czas jednej klatki
            if self._timer >= self._wait_time:
                self.save_high_score()
                next_state = "END_LEVEL"
        return next_state

    def draw(self, screen):
        super().draw(screen)
        self._draw_trajectory(screen)
        self._slingshot.draw(screen)


class PauseState(State):
    def __init__(self, screen_size: pygame.Vector2, paused_state: State):
        self._paused_state = paused_state
        with open('objects_config_files/pause.json') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()

    def get_paused_state(self) -> GameState:
        return self._paused_state

    def get_level(self) -> int:
        return self._paused_state.get_level()

    def _create_buttons(self):
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._settings_button = self._buttons_dict['settings_button']
        self._quit_button = self._buttons_dict['quit_button']

    def _handle_input(self, events: list) -> str:
        if self._play_button.is_clicked(events):
            return "UNPAUSE_GAME"
        if self._retry_button.is_clicked(events):
            return 'RESTART_LEVEL'
        if self._settings_button.is_clicked(events):
            pass
        if self._quit_button.is_clicked(events):
            return "GO_TO_MENU"

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "UNPAUSE_GAME"

    def update(self, events: list) -> str:
        next_state = self._handle_input(events)
        return next_state

    def draw(self, screen):
        self._paused_state.draw(screen)
        self._draw_objects(screen)


class LevelCompleteState(State):
    def __init__(self, screen_size: pygame.Vector2, completed_level: State):

        scores = completed_level.get_scores()
        self._current_score, self._high_score = scores
        self._completed_level = completed_level
        self._level = self._completed_level.get_level()

        path = 'objects_config_files/level_summary.json'
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()

        self._update_score_labels(self._current_score,
                                  self._high_score)

    def get_completed_level_state(self) -> State:
        return self._completed_level

    def get_level(self) -> State:
        return self._level

    def _create_buttons(self):
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._quit_button = self._buttons_dict['quit_button']

    def _handle_input(self, events: list) -> str:
        next_state = self
        if self._play_button.is_clicked(events):
            if self._current_score > 0:
                next_state = 'NEXT_LEVEL'
            else:
                next_state = 'RESTART_LEVEL'
        elif self._retry_button.is_clicked(events):
            next_state = 'RESTART_LEVEL'
        elif self._quit_button.is_clicked(events):
            next_state = "GO_TO_MENU"
        return next_state

    def update(self, events):
        next_state = self._handle_input(events)
        return next_state

    def draw(self, screen):
        self._completed_level.draw(screen)

        overlay = pygame.Surface((self._screen_size.x / 2,
                                  self._screen_size.y),
                                 pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        overlay_rect = overlay.get_rect()
        overlay_rect.center = (self._screen_size / 2)
        screen.blit(overlay, overlay_rect)

        self._draw_objects(screen)
        self._draw_texts(screen)
