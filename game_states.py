import helpers
import pymunk
import pygame
import json


class GameObject:
    def __init__(self, pos, size, img_path):
        helpers.check_size(size)
        self._image = self.load_image(img_path, size)
        self._object_rect = self._image.get_rect()
        self._object_rect.center = pos

    def position(self):
        return self._object_rect.center

    def load_image(self, img_path, img_size=None):
        return helpers.load_image(img_path, img_size)

    def draw(self, screen):
        screen.blit(self._image, self._object_rect)


class Slingshot(GameObject):
    def __init__(self, data):
        object_data = data['slingshot']
        self._name = object_data['name']
        self._height = object_data['height']
        self._width = self._height / 1.54
        self._size = (self._width, self._height)
        self._pos = (object_data['pos_x'], object_data['pos_y'])

        self._rubber_color = (object_data['color_R'], object_data['color_G'],
                              object_data['color_B'])
        self._img_path = object_data['img_path']
        super().__init__(self._pos, self._size, self._img_path)


class Projectile(GameObject):
    def __init__(self, space, object_data, position):
        self._name = object_data['name']
        self._mass = object_data['mass']
        self._radius = object_data['radius']
        self._pos = position
        self._img_path = object_data['img_path']

        self._create_object(space)
        diameter = int(2*self._shape.radius)
        self._size = (diameter, diameter)
        super().__init__(self._pos, self._size, self._img_path)

    def _create_object(self, space):
        # oblicza moment bezwladności
        self._moment = pymunk.moment_for_circle(self._mass, 0, self._radius)
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.STATIC)
        self._body.position = self._pos
        self._shape = pymunk.Circle(self._body, self._radius)
        space.add(self._body, self._shape)

    def launch(self, impulse_vector):
        self._body.body_type = pymunk.Body.DYNAMIC
        self._body.mass = self._mass
        self._body.moment = self._moment

        self._body.apply_impulse_at_local_point(impulse_vector)

    def is_dragged(self, events):
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            m_collision = self._object_rect.collidepoint(mouse_pos)
            if m_collision and self._body.body_type == pymunk.Body.STATIC:
                return True
        return False

    def drag(self):
        pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        self._body.position = pos

    def body(self):
        return self._body

    def shape(self):
        return self._shape

    def update(self):
        pos_x = int(self._body.position.x)
        pos_y = int(self._body.position.y)
        self._object_rect.center = (pos_x, pos_y)

    def draw(self, screen):
        screen.blit(self._image, self._object_rect)


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


class GameState(State):
    def __init__(self, screen_size, level):
        super().__init__(screen_size)
        self._level = level
        self._space = pymunk.Space()
        self._space.gravity = (50, 900)
        self._slingshot_pos = (700, 800)
        self._objects = self._initialize_objects()

        self._ammo_pointer = 0
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
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                dis_x = abs(self._slingshot_pos[0] -
                            self._objects[0].position()[0])
                dis_y = abs(self._slingshot_pos[1] -
                            self._objects[0].position()[1])
                distance = max(dis_x, dis_y)
                if self._dragged_object is not None and distance <= 5000:
                    object_pos_x = self._objects[0].position()[0]
                    object_pos_y = self._objects[0].position()[1]
                    direction_x = self._slingshot_pos[0] - object_pos_x
                    direction_y = self._slingshot_pos[1] - object_pos_y

                    self._objects[self._ammo_pointer].launch((direction_x*6.5,
                                                              direction_y*6.5))

        if self._objects[0].is_dragged(events):
            self._dragged_object = self._objects[self._ammo_pointer]
            self._objects[0].drag()
        else:
            self._dragged_object = None

        return None

    def draw_objects(self, screen):
        for object in self._objects:
            object.draw(screen)

    def update(self, events):
        self._space.step(1/60)
        for object in self._objects:
            object.update()

        if self._check_for_launch(events) is not None:
            self._objects[0].launch(self._check_for_launch)

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
