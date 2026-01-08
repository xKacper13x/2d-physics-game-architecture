from entities.objects_base import GameObject
import pymunk
import pygame


class Slingshot(GameObject):
    def __init__(self, data):
        object_data = data['slingshot']
        self._pos = (object_data['pos_x'], object_data['pos_y'])
        super().__init__(object_data)
        self._power = object_data['power']

        self._rubber_color = (object_data['color_R'], object_data['color_G'],
                              object_data['color_B'])
        self._rubber_width = object_data['rubber_width']

        self._left_fork_offset = pygame.math.Vector2(self._width / -4.15,
                                                     self._height / -3)
        self._right_fork_offset = pygame.math.Vector2(self._width / 4.15,
                                                      self._height / -2.6)

    def get_power(self) -> int:
        return self._power

    def get_height(self):
        return self._height

    def draw_outer_rubber(self, screen, projectile_pos=None):
        left_fork = self._pos + self._left_fork_offset
        if projectile_pos is None:
            right_fork = self._pos + self._right_fork_offset
            pygame.draw.line(screen, self._rubber_color, left_fork,
                             right_fork, self._rubber_width)
        else:
            pygame.draw.line(screen, self._rubber_color, left_fork,
                             projectile_pos, self._rubber_width)

    def draw_inner_rubber(self, screen, projectile_pos):
        right_fork = self._pos + self._right_fork_offset
        pygame.draw.line(screen, self._rubber_color, right_fork,
                         projectile_pos, self._rubber_width)


class Ground:
    def __init__(self, screen_size: pygame.Vector2, y_pos: int, space):
        self._width = 3 * screen_size[0]
        self._y_pos = y_pos

        self._start_point = (-350, self._y_pos)
        self._end_point = (self._width, self._y_pos)
        self._create_physics(space)

    def get_pos_y(self):
        return self._y_pos

    def _create_physics(self, space):
        self._body = space.static_body

        self._shape = pymunk.Segment(self._body, self._start_point,
                                     self._end_point, 5)

        # Właściwości fizyczne
        # Maksymalne tarcie (żeby elementy się nie ślizgały jak na lodzie)
        self._shape.friction = 1.0

        # Mała sprężystość (żeby nie odbijały się jak od trampoliny)
        self._shape.elasticity = 0.2

        space.add(self._shape)
