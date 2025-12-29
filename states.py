from game_objects import Projectile, Slingshot
import buttons
import pygame
import pymunk
import helpers
import json


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
        self._space = pymunk.Space()
        self._space.gravity = (50, 900)
        self._slingshot_pos = (700, 800)
        self._objects = self._initialize_objects()

        self._ammo_pointer = 0
        self._object_on_sling = self._projectiles[self._ammo_pointer]
        self._dragged_object = None

    def _initialize_objects(self):
        path = f'objects_config_files/level{self._level}.json'
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            self._set_background(data)

            self._slingshot = Slingshot(data)
            slingshot_x = self._slingshot.position()[0]
            slingshot_y = self._slingshot.position()[1] - 95
            self._slingshot_pos = (slingshot_x, slingshot_y)

            self._projectiles = self._initialize_projectiles(data)
        return self._projectiles

    def _initialize_projectiles(self, data):
        all_projectiles = data['projectiles']
        objects = []
        for projectile in all_projectiles:
            object = Projectile(self._space, projectile, self._slingshot_pos)
            objects.append(object)

        return objects

    def _check_for_launch(self, events):
        dis_x = abs(self._slingshot_pos[0] -
                    self._objects[0].position()[0])
        dis_y = abs(self._slingshot_pos[1] -
                    self._objects[0].position()[1])
        distance = max(dis_x, dis_y)
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self._dragged_object is not None:
                    if distance >= 50:
                        object_pos_x = self._objects[0].position()[0]
                        object_pos_y = self._objects[0].position()[1]
                        direct_x = self._slingshot_pos[0] - object_pos_x
                        direct_y = self._slingshot_pos[1] - object_pos_y

                        self._objects[self._ammo_pointer].launch(
                                                                (direct_x*6.5,
                                                                 direct_y*6.5))
                    if distance < 80:
                        self._objects[self._ammo_pointer].go_to_start_pos()

        if self._objects[0].is_dragged() and distance <= 5000:
            self._dragged_object = self._objects[self._ammo_pointer]
            self._objects[0].drag()
        else:
            self._dragged_object = None

        return None

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

    def update(self, events):
        self._space.step(1/60)
        for object in self._objects:
            object.update()

        if self._check_for_launch(events) is not None:
            self._objects[0].launch(self._check_for_launch)

        if self._projectiles[self._ammo_pointer].is_on_sling():
            self._object_on_sling = self._projectiles[self._ammo_pointer]
        else:
            self._object_on_sling = None

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
