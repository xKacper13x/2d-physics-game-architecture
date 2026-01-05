from entities.objects_base import PhysicalObject
from entities.static_objects import Slingshot, Ground
from entities.enemy import Enemy
from entities.projectile import Projectile
from entities.structure import Structure
import pygame
import pymunk
import json
import math
import helpers
import entities.ui_elements as ui_elements


class State:
    def __init__(self, screen_size, data):
        self._screen_size = screen_size

        self._buttons_dict = {}
        self._texts_dict = {}
        self._objects = self._initialize_objects(data)
        self._texts = self._initialize_texts(data)

    def _initialize_objects(self, data):
        result = []

        objects_data = data['objects']
        if 'buttons' in objects_data:
            self._buttons = self._initialize_buttons(objects_data)
            result += self._buttons

        return result

    def _initialize_texts(self, data):
        created_texts = []
        if 'texts' in data:
            object_data = data['texts']

            created_texts = []
            for obj in object_data:
                text = ui_elements.Text(obj, self._screen_size)

                created_texts.append(text)
                self._texts_dict[text.name()] = text
        return created_texts

    def _initialize_buttons(self, data):
        object_data = data['buttons']

        created_buttons = []
        for obj in object_data:
            if 'texts' in obj.keys():
                button = ui_elements.TextButton(obj, self._screen_size)
            else:
                button = ui_elements.Button(obj, self._screen_size)

            created_buttons.append(button)
            self._buttons_dict[button.name()] = button
        return created_buttons

    def _set_background(self, img_path):
        self._background_image = self.load_image(img_path)

    def load_image(self, img_path, img_size=None):
        if img_size is None:
            img_size = self._screen_size
        return helpers.load_image(img_path, img_size)

    def _draw_objects(self, screen):
        for obj in self._objects:
            obj.draw(screen)

    def _draw_texts(self, screen):
        for text in self._texts:
            text.draw(screen)

    def update(self, events):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))
        screen.blit(self._background_image, (0, 0))
        self._draw_objects(screen)
        self._draw_texts(screen)


class MainMenuState(State):
    def __init__(self, screen_size):
        with open('objects_config_files/menu.json') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()
            background_img_path = data["background_img"]
            self._set_background(background_img_path)

    def _create_buttons(self):
        self._play_button = self._buttons_dict['play_menu_button']
        self._options_button = self._buttons_dict['options_menu_button']
        self._quit_button = self._buttons_dict['quit_menu_button']

    def update(self, events):
        next_state = self
        if self._play_button.is_clicked(events):
            next_state = 'START_GAME'
        elif self._options_button.is_clicked(events):
            pass
            new_event = pygame.event.Event(pygame.KEYDOWN)
            new_event.key = pygame.K_F11
            pygame.event.post(new_event)
            # next_state SettingsState(self._screen_size)
        elif self._quit_button.is_clicked(events):
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
        return next_state


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
            self._create_texts()

        self._current_score = 0
        initial_text = self._score_text.get_initial_text()
        new_text = initial_text + f' {self._current_score:^5}'
        self._score_text.set_text(new_text)

        initial_text = self._high_score_text.get_initial_text()
        new_text = initial_text + f' {self._high_score:^5}'
        self._high_score_text.set_text(new_text)

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

    def _create_buttons(self):
        self._pause_button = self._buttons_dict['pause_button']

    def _create_texts(self):
        self._score_text = self._texts_dict['score_text']
        self._high_score_text = self._texts_dict['high_score_text']

    def _initialize_objects(self, data):
        objects = super()._initialize_objects(data)
        data = data['objects']
        self._slingshot = Slingshot(data)
        slingshot_x = self._slingshot.position()[0]
        slingshot_y = self._slingshot.position()[1] - 95
        self._slingshot_pos = (slingshot_x, slingshot_y)

        self._projectiles_data = data['projectiles']
        self._current_projectile = self._initialize_projectile()
        objects.append(self._current_projectile)
        self._enemies = self._initialize_enemies(data)
        self._structures = self._initialize_structures(data)
        return objects + self._enemies + self._structures

    def _initialize_projectile(self) -> Projectile:
        data = self._projectiles_data[self._ammo_pointer]
        projectile = Projectile(self._space, data, self._slingshot_pos)
        return projectile

    def _initialize_enemies(self, data):
        all_enemies = data['enemies']
        objects = []
        for enemy in all_enemies:
            object = Enemy(self._space, enemy)
            objects.append(object)

        return objects

    def _initialize_structures(self, data):
        all_structures = data['structures']
        objects = []
        for structure in all_structures:
            object = Structure(self._space, structure)
            objects.append(object)

        return objects

    def _check_for_launch(self, events):
        object_pos_x = self._current_projectile.position()[0]
        object_pos_y = self._current_projectile.position()[1]

        dis_x = self._slingshot_pos[0] - object_pos_x
        dis_y = self._slingshot_pos[1] - object_pos_y
        distance = math.dist(self._slingshot_pos,
                             self._current_projectile.position())

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self._dragged_object is not None:
                    if distance >= 70:
                        power = self._slingshot.get_power()
                        self._current_projectile.launch(
                                                                (dis_x*power,
                                                                 dis_y*power))
                    else:
                        self._current_projectile.go_to_start_pos()
                    self._dragged_object = None

        is_ammo_dragged = self._current_projectile.is_dragged()
        if is_ammo_dragged or self._dragged_object is not None:
            self._dragged_object = self._current_projectile
            self._dragged_object.drag(self._slingshot_pos, self._max_dis)
        elif not pygame.mouse.get_pressed()[0]:
            self._dragged_object = None

    def _draw_objects(self, screen):
        # Rysowanie warstwowe (Proca Tył -> Ptak -> Proca Przód)
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
        if type(obj_to_remove).__name__ == 'Enemy':
            self._enemies.remove(obj_to_remove)

    def _end_level(self):
        if self._enemies:
            self._current_score = 0
        self._timer = 0
        self._level_ended = True

    def _create_end_game_state(self) -> State:
        scores = (self._current_score, self._high_score)
        return LevelCompleteState(self._screen_size,
                                  scores,
                                  self)

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

        start_x, start_y = self._current_projectile.position()
        sling_x, sling_y = self._slingshot_pos

        diff_x = sling_x - start_x
        diff_y = sling_y - start_y

        power = self._slingshot.get_power()

        impulse_x = diff_x * power
        impulse_y = diff_y * power

        mass = self._current_projectile.get_mass()

        if mass == 0:
            mass = 1

        vel_x = impulse_x / mass
        vel_y = impulse_y / mass

        # Symulacja trajektorii
        gravity_x, gravity_y = self._space.gravity
        point_count = 30
        time_step = 0.08

        for i in range(1, point_count):
            t = i * time_step + time_step

            # Wzór na pozycję: s = s0 + vt + 0.5at^2
            curr_x = start_x + (vel_x * t) + (0.5 * gravity_x * t * t)
            curr_y = start_y + (vel_y * t) + (0.5 * gravity_y * t * t)

            if curr_y > self._ground.get_pos_y():
                break
            elif curr_x > self._screen_size[0] / 2:
                break

            # Rysowanie kropki
            radius = 5 - (i // 10)
            radius = max(radius, 2)

            pygame.draw.circle(screen, (255, 255, 255), (int(curr_x),
                                                         int(curr_y)), radius)
            pygame.draw.circle(screen, (0, 0, 0), (int(curr_x), int(curr_y)),
                               radius, 1)

    def update(self, events: list) -> State:
        self._space.step(1/60)

        if not self._level_ended:
            self._check_for_launch(events)

        if self._current_projectile.is_on_sling(self._slingshot_pos,
                                                self._max_dis):
            self._object_on_sling = self._current_projectile
        else:
            self._object_on_sling = None

        objects_to_kill = []
        for obj in self._objects:
            killable_objects = ['Enemy', 'Structure']
            if type(obj).__name__ in killable_objects:
                objects_to_kill = obj.update(objects_to_kill)
                self._current_score += obj.collect_points()

                initial_text = self._score_text.get_initial_text()
                new_text = initial_text + f' {self._current_score:^5}'
                self._score_text.set_text(new_text)
                if self._current_score > self._high_score:
                    initial_text = self._high_score_text.get_initial_text()
                    new_text = initial_text + f' {self._high_score:^5}'
                    self._high_score_text.set_text(new_text)
            else:
                obj.update()

        for obj in objects_to_kill:
            self._kill_object(obj)

        if not self._enemies and not self._level_ended:
            self._end_level()

        if not self._current_projectile.is_on_sling(self._slingshot_pos,
                                                    self._max_dis):
            if not self._projectile_stopped:
                real_velocity = pygame.Vector2(
                    self._current_projectile.velocity()).length()
                is_stopped = real_velocity < 4
                is_off_screen = self._current_projectile.off_screen(
                                                            self._screen_size)

                if is_stopped or is_off_screen:
                    self._projectile_stopped = True
                    self._timer = 0

            self._timer += 1/60
            if self._projectile_stopped and self._timer >= 2:
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

        if self._pause_button.is_clicked(events):
            return PauseState(self._screen_size, self)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return PauseState(self._screen_size, self)

        next_state = self
        if self._level_ended:
            self._timer += 1/60  # Dodajemy czas jednej klatki
            if self._timer >= self._wait_time:
                self.save_high_score()
                next_state = self._create_end_game_state()
        return next_state

    def draw(self, screen):
        super().draw(screen)
        self._draw_trajectory(screen)
        self._slingshot.draw(screen)


class LevelCompleteState(State):
    def __init__(self, screen_size, scores: tuple, completed_level: State):

        self._score, self._high_score = scores
        self._completed_level = completed_level
        self._level = self._completed_level.get_level()

        path = 'objects_config_files/level_summary.json'
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()
            self._create_texts()

        new_text = self._score_text.get_initial_text() + f' {self._score:^5}'
        self._score_text.set_text(new_text)

        initial_text = self._high_score_text.get_initial_text()
        new_text = initial_text + f' {self._high_score:^5}'
        self._high_score_text.set_text(new_text)

    def _create_buttons(self):
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._quit_button = self._buttons_dict['quit_button']

    def _create_texts(self):
        self._score_text = self._texts_dict['score_text']
        self._high_score_text = self._texts_dict['high_score_text']

    def update(self, events):
        next_state = self
        if self._play_button.is_clicked(events):
            if self._score > 0:
                next_state = GameState(self._screen_size, 1)
        elif self._retry_button.is_clicked(events):
            next_state = GameState(self._screen_size, self._level)
        elif self._quit_button.is_clicked(events):
            next_state = "GO_TO_MENU"
        return next_state

    def draw(self, screen):
        self._completed_level.draw(screen)
        middle_x, middle_y = self._screen_size / 2
        x_offset = 450
        y_offset = 450

        left_top = (middle_x - x_offset, middle_y - y_offset)
        right_top = (middle_x + x_offset, middle_y - y_offset)
        left_bottom = (middle_x - x_offset, middle_y + y_offset)
        right_bottom = (middle_x + x_offset, middle_y + y_offset)

        BLACK = (0, 0, 0)
        points = [left_top, right_top, right_bottom, left_bottom]
        pygame.draw.polygon(screen, BLACK, points)
        self._draw_objects(screen)
        self._draw_texts(screen)


class PauseState(State):
    def __init__(self, screen_size: pygame.Vector2, paused_state: State):
        self._paused_state = paused_state
        with open('objects_config_files/pause.json') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()

    def _create_buttons(self):
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._settings_button = self._buttons_dict['settings_button']
        self._quit_button = self._buttons_dict['quit_button']

    def update(self, events):
        if self._play_button.is_clicked(events):
            return self._paused_state
        if self._retry_button.is_clicked(events):
            return GameState(self._screen_size, self._paused_state.get_level())
        if self._settings_button.is_clicked(events):
            pass
        if self._quit_button.is_clicked(events):
            return "GO_TO_MENU"

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return self._paused_state
        return self

    def draw(self, screen):
        self._paused_state.draw(screen)
        self._draw_objects(screen)
