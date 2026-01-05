from entities.objects_base import PhysicalObject
import pymunk
import pygame


class Structure(PhysicalObject):
    def __init__(self, space, object_data):
        self._pos = (object_data['pos_x'], object_data['pos_y'])
        super().__init__(space, object_data)
        self._mass = object_data['mass']

        self._img_path = object_data['img_path']
        self._create_physics(space)

    def _create_physics(self, space):
        # oblicza moment bezwladności
        self._moment = pymunk.moment_for_box(self._mass, self._size)
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.DYNAMIC)
        self._body.position = self._pos
        self._shape = pymunk.Poly.create_box(self._body, self._size)

        self._shape.friction = 0.5
        self._shape.elasticity = 0.1
        self._shape.game_object = self

        space.add(self._body, self._shape)

    def update(self, objects_to_kill: list = None):
        if objects_to_kill is None:
            raise ValueError('update() method requires objects_to_kill_list')
        return super().update(objects_to_kill)

    def draw(self, screen):
        p = self._body.position

        # Konwersja lokalnych wierzchołków Pymunk na świat gry
        # self._shape to Poly
        points = []
        for v_local in self._shape.get_vertices():
            # Obrót i przesunięcie punktu
            v_rot = v_local.rotated(self._body.angle)
            p_world = p + v_rot
            points.append(p_world)

        # Rysujemy wielokąt (polygon) łączący te 4 punkty
        pygame.draw.polygon(screen, (139, 69, 19), points)
        # Opcjonalnie czarna obwódka
        pygame.draw.polygon(screen, (0, 0, 0), points, 2)
