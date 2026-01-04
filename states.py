from game_objects import (Projectile, Slingshot, Structure,
                          Ground, Enemy, PhysicalObject)
import buttons
import pygame
import pymunk
import helpers
import json
import math


class State:
    def __init__(self, screen_size):
        self._screen_size = screen_size

    def _set_background(self, data):
        background_img_path = data["background_img"]
        self._background_image = self.load_image(
            background_img_path)

    def load_image(self, img_path, img_size=None):
        if img_size is None:
            img_size = self._screen_size
        return helpers.load_image(img_path, img_size)

    def update(self, events):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))
        screen.blit(self._background_image, (0, 0))


class MainMenuState(State):
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.pressed_keys = []

        with open('objects_config_files/menu.json') as file_handle:
            data = json.load(file_handle)
            self._set_background(data)
        self.create_buttons(screen_size)

    def create_buttons(self, screen_size):
        y_pos = 470
        center_x = screen_size[0] * 0.5
        spacing = 300
        size = pygame.Vector2(175, 175)
        path = 'assets/images/Title_Screen_button.png'
        font_path = 'assets/fonts/Dalek.ttf'
        font_size = 35

        pos = pygame.Vector2(center_x - spacing, y_pos)
        self._play_button = buttons.Button(pos, size, path)
        self._play_button.add_text('PLAY', font_path, font_size)

        pos = pygame.Vector2(center_x, y_pos)
        self._settings_button = buttons.Button(pos, size, path)
        self._settings_button.add_text('OPTIONS', font_path, font_size)

        pos = pygame.Vector2(center_x + spacing, y_pos)
        self._quit_button = buttons.Button(pos, size, path)
        self._quit_button.add_text('QUIT', font_path, font_size)

    def update(self, events):
        next_state = self
        if self._play_button.is_clicked(events):
            next_state = GameState(self._screen_size, 1)
        elif self._settings_button.is_clicked(events):
            pass
            new_event = pygame.event.Event(pygame.KEYDOWN)
            new_event.key = pygame.K_F11
            pygame.event.post(new_event)
            # next_state SettingsState(self._screen_size)
        elif self._quit_button.is_clicked(events):
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
        return next_state

    def draw(self, screen):
        super().draw(screen)
        self._play_button.draw(screen)
        self._settings_button.draw(screen)
        self._quit_button.draw(screen)


class GameState(State):
    def __init__(self, screen_size, level):
        super().__init__(screen_size)
        self._level = level
        self._ammo_pointer = 0

        self._space = pymunk.Space()
        self._space.gravity = (50, 900)

        self._slingshot_pos = (700, 800)
        self._high_score = 0
        self._current_score = 0
        self._objects = self._initialize_objects()
        self._max_dis = self._slingshot._height * 0.8

        self._object_on_sling = self._current_projectile
        self._dragged_object = None
        self._ground = Ground(self._screen_size, 920, self._space)

    def _initialize_objects(self):
        path = f'objects_config_files/level{self._level}.json'
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            self._set_background(data)
            self._high_score = data['high_score']

            self._slingshot = Slingshot(data)
            slingshot_x = self._slingshot.position()[0]
            slingshot_y = self._slingshot.position()[1] - 95
            self._slingshot_pos = (slingshot_x, slingshot_y)

            self._projectiles_data = data['projectiles']
            self._current_projectile = self._initialize_projectile()
            self._enemies = self._initialize_enemies(data)
            self._structures = self._initialize_structures(data)
        return [self._current_projectile] + self._structures + self._enemies

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
                        self._current_projectile.launch(
                                                                (dis_x*6.7,
                                                                 dis_y*6.7))
                    else:
                        self._current_projectile.go_to_start_pos()
                    self._dragged_object = None

        is_ammo_dragged = self._current_projectile.is_dragged()
        if is_ammo_dragged or self._dragged_object is not None:
            self._dragged_object = self._current_projectile
            self._dragged_object.drag(self._slingshot_pos, self._max_dis)
        elif not pygame.mouse.get_pressed()[0]:
            self._dragged_object = None

    def draw_objects(self, screen):
        # Rysowanie warstwowe (Proca Tył -> Ptak -> Proca Przód)
        if self._object_on_sling is not None:
            rubber_anchor = self._object_on_sling.get_rubber_anchor()
            self._slingshot.draw_inner_rubber(screen,
                                              rubber_anchor)
            for object in self._objects:
                object.draw(screen)
            self._slingshot.draw_outer_rubber(screen,
                                              rubber_anchor)
        else:
            self._slingshot.draw_outer_rubber(screen)
            for object in self._objects:
                object.draw(screen)

    def _kill_object(self, obj_to_remove: PhysicalObject) -> None:
        space_bodies = self._space.bodies
        if obj_to_remove._body in space_bodies:
            self._space.remove(obj_to_remove._body, obj_to_remove._shape)
        if obj_to_remove in self._objects:
            self._objects.remove(obj_to_remove)

    def _end_level(self):
        print(f'Final score : {self._current_score}')

    def update(self, events):
        self._space.step(1/60)

        self._check_for_launch(events)

        if self._current_projectile.is_on_sling(self._slingshot_pos,
                                                self._max_dis):
            self._object_on_sling = self._current_projectile
        else:
            self._object_on_sling = None

        objects_to_kill = []
        for object in self._objects:
            if type(object).__name__ == 'Enemy':
                objects_to_kill = object.update(objects_to_kill)
            else:
                object.update()

            if hasattr(object, 'collect_points'):
                self._current_score += object.collect_points()

        for object in objects_to_kill:
            self._kill_object(object)
        self._high_score = max(self._high_score, self._current_score)

        if not self._current_projectile.is_on_sling(self._slingshot_pos,
                                                    self._max_dis):

            real_velocity = pygame.Vector2(self._current_projectile.velocity()).length()
            is_stopped = real_velocity < 2
            is_off_screen = self._current_projectile.off_screen(
                                                            self._screen_size)
            if is_stopped or is_off_screen:
                self._ammo_pointer += 1
                self._kill_object(self._current_projectile)
                if self._ammo_pointer >= len(self._projectiles_data):
                    self._end_level()
                else:
                    self._current_projectile = self._initialize_projectile()
                    self._objects.append(self._current_projectile)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Zapauzowanie gry i wyświetlenie menu
                pass
        return self

    def draw(self, screen):
        # Czyści ekran
        super().draw(screen)
        self.draw_objects(screen)
        self._slingshot.draw(screen)
