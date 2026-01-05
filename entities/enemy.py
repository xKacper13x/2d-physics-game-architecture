from entities.objects_base import PhysicalObject
import pymunk


class Enemy(PhysicalObject):
    def __init__(self, space, object_data):
        self._pos = (object_data['pos_x'], object_data['pos_y'])
        super().__init__(space, object_data)

        self._mass = object_data['mass']

        self._create_physics(space)

    def _create_physics(self, space):
        # oblicza moment bezwladności
        self._moment = pymunk.moment_for_box(self._mass, self._size)
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.DYNAMIC)
        self._body.position = self._pos
        self._shape = pymunk.Poly.create_box(self._body, (self._width * 0.8,
                                                          self._height))
        self._shape.friction = 0.5
        self._shape.elasticity = 0.1
        space.add(self._body, self._shape)

    def update(self, objects_to_kill: list = None):
        if objects_to_kill is None:
            raise ValueError('update() method requires objects_to_kill_list')

        contacts = self._space.shape_query(self._shape)
        for contact in contacts:
            other_shape = contact.shape
            if hasattr(other_shape, 'game_object'):
                who_hit_me = other_shape.game_object

                if type(who_hit_me).__name__ == 'Projectile':
                    self._health = 0
                    self._score += 1000

        return super().update(objects_to_kill)