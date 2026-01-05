import pygame
import helpers
import math


class GameObject:
    def __init__(self, object_data: dict) -> None:
        self._name = object_data['name']
        self._img_path = object_data['img_path']

        if 'height' in object_data:
            self._height = int(object_data['height'])
            if 'width' in object_data:
                self._width = int(object_data['width'])
                self._size = (self._width, self._height)
                self._image = self._load_image(self._img_path, self._size)
            else:
                self._image = self._load_image(self._img_path, self._height)
                self._width = self._image.get_width()
                self._size = (self._width, self._height)
        else:
            self._radius = int(object_data['radius'])
            diameter = int(2*self._radius)
            self._size = (diameter, diameter)

            helpers.check_size(self._size)
            self._image = self._load_image(self._img_path, self._size)

        self._object_rect = self._image.get_rect()
        self._object_rect.center = self._pos

    def name(self) -> str:
        return self._name

    def position(self):
        return self._object_rect.center

    def _load_image(self, img_path, img_size=None):
        return helpers.load_image(img_path, img_size)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._image, self._object_rect)

    def update(self, objects_to_kill: list = None):
        pass


class PhysicalObject(GameObject):
    def __init__(self, space, object_data):
        self._space = space
        self._mass = object_data['mass']

        if object_data['health'] == 'inf':
            self._health = math.inf
        else:
            self._health = object_data['health']

        super().__init__(object_data)
        self._score = 0
        self._max_x = self._pos[0] + 100
        self._original_image = self._image

        self._last_velocity = pygame.Vector2(0, 0)

    def get_mass(self):
        return self._mass

    def collect_points(self) -> int:
        points = self._score
        self._score = 0
        return points

    def _take_damage(self, damage):
        new_health = self._health - abs(damage)
        self._score += int(abs(damage) * 3)
        self._health = max(new_health, 0)

    def off_screen(self, screen_size) -> bool:
        max_x = screen_size[0]
        off_screen = False
        if self._body.position.x > max_x + 300 or self._body.position.x < -300:
            off_screen = True

        return off_screen

    def velocity(self):
        return self._body.velocity

    def update(self, objects_to_kill: list = None):
        pos_x = int(self._body.position.x)
        pos_y = int(self._body.position.y)
        self._object_rect.center = (pos_x, pos_y)
        if objects_to_kill is None:
            return None
        if self in objects_to_kill:
            return objects_to_kill

        current_velocity = self._body.velocity
        impact_velocity = current_velocity - self._last_velocity
        self._last_velocity = pygame.Vector2(current_velocity.x,
                                             current_velocity.y)

        impact_force = impact_velocity.length
        DAMAGE_THRESHOLD = 300

        if impact_force > DAMAGE_THRESHOLD:
            damage_to_deal = impact_force * 0.3
            self._take_damage(damage_to_deal)

        if self._body.position.x > self._max_x:
            self._health = 0
            self._score += 700

        if self._health == 0:
            objects_to_kill.append(self)
        return objects_to_kill

    def draw(self, screen: pygame.Surface) -> None:
        angle = self._body.angle
        angle = -1 * math.degrees(angle)
        self._image = pygame.transform.rotate(self._original_image, angle)
        pos = self._body.position
        self._object_rect = self._image.get_rect(center=(pos.x, pos.y))
        super().draw(screen)
        self._max_x = screen.get_width()
