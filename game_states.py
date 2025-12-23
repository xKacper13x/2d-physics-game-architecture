import helpers
import pymunk
import pygame


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


class Projectile(GameObject):
    def __init__(self, space, pos, img_path, size=None):
        self._create_object(space, pos)
        diameter = int(2*self._shape.radius)
        size = (diameter, diameter)
        super().__init__(pos, size, img_path)

    def _create_object(self, space, pos):
        mass = 1
        radius = 40
        # oblicza moment bezwladności
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self._body = pymunk.Body(mass, moment)
        self._body.position = pos
        self._shape = pymunk.Circle(self._body, radius)
        space.add(self._body, self._shape)

    def launch(self, impulse_vector):
        self._body.apply_impulse_at_local_point(impulse_vector)

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

    def load_image(self, img_path, img_size=None):
        if img_size is None:
            img_size = self._screen_size
        return helpers.load_image(img_path, img_size)

    def update(self, events):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))


class GameState(State):
    def __init__(self, screen_size, level):
        super().__init__(screen_size)
        self._level = level
        self._space = pymunk.Space()
        self._space.gravity = (50, 900)
        self._objects = self.initialize_objects()

    def initialize_objects(self):
        rock = Projectile(self._space, (300, 0), 'assets/images/rock.png')

        objects = []
        objects.append(rock)
        return objects

    def draw_objects(self, screen):
        for object in self._objects:
            object.draw(screen)

    def update(self, events):
        self._space.step(1/60)
        for object in self._objects:
            object.update()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._objects[0].launch((2000, -2000))
        return self

    def draw(self, screen):
        # Czyści ekran
        super().draw(screen)
        self.draw_objects(screen)
