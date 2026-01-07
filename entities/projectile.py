from entities.objects_base import PhysicalObject
import pygame
import pymunk


class Projectile(PhysicalObject):
    def __init__(self, space, object_data, position):
        self._mass = object_data['mass']

        self._pos = position
        super().__init__(space, object_data)
        self._score = object_data['score']
        self._pull_vector = pygame.Vector2(0, 0)

        self._create_physics(space)

    def _create_physics(self, space):
        # oblicza moment bezwladności
        self._moment = 999990
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.STATIC)
        self._body.position = self._pos
        self._shape = pymunk.Circle(self._body, self._radius)

        self._shape.friction = 1.0
        self._shape.elasticity = 0.7
        self._shape.game_object = self

        space.add(self._body, self._shape)

    def launch(self, impulse_vector):
        self._body.body_type = pymunk.Body.DYNAMIC
        self._body.mass = self._mass
        self._body.moment = self._moment

        self._body.apply_impulse_at_local_point(impulse_vector)
        start_vec = pygame.math.Vector2(self._pos)
        current_vec = pygame.math.Vector2(self.position())

        self._pull_vector = current_vec - start_vec

    def go_to_start_pos(self):
        self._body.position = self._pos

    def is_dragged(self) -> bool:
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            m_collision = self._object_rect.collidepoint(mouse_pos)
            if m_collision and self._body.body_type == pymunk.Body.STATIC:
                return True
        return False

    def is_on_sling(self, slingshot_pos, max_distance) -> bool:
        if self._body.body_type != pymunk.Body.DYNAMIC:
            return True
        # elif self._body.body_type == pymunk.Body.DYNAMIC:
        #     return False

        slingshot_center = pygame.math.Vector2(self._pos)
        current_pos = pygame.math.Vector2(self.position())
        current_vector = current_pos - slingshot_center

        # 3. ILOCZYN SKALARNY (Dot Product)
        # Sprawdzamy kąt między "Wektorem Naciągu" a "Aktualnym Wektorem".
        # Jeśli wynik > 0:
        # Pocisk jest nadal po stronie naciągu (Leci do procy).
        # Jeśli wynik < 0:
        # Pocisk minął środek procy i leci w świat (Guma znika).
        dot_product = current_vector.dot(self._pull_vector)
        vector = self._distance_to_slingshot(slingshot_pos)
        if dot_product > 0 and vector.length() <= max_distance:
            return True
        else:
            return False

    def _distance_to_slingshot(self, slingshot_pos):
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        sling_x = slingshot_pos[0]
        sling_y = slingshot_pos[1]

        vector = pygame.Vector2(mouse_x - sling_x, mouse_y - sling_y)
        return vector

    def drag(self, slingshot_pos, max_distance):
        vector = self._distance_to_slingshot(slingshot_pos)
        if vector.length() > max_distance:
            vector.scale_to_length(max_distance)

        new_pos = pygame.Vector2(slingshot_pos) + vector
        self._body.position = tuple(new_pos)

    def body(self):
        return self._body

    def shape(self):
        return self._shape

    def get_rubber_anchor(self) -> tuple:
        projectile_center = pygame.math.Vector2(self.position())
        slingshot_center = pygame.math.Vector2(self._pos)

        direction = slingshot_center - projectile_center

        # Zabezpieczenie: jeśli ptak jest idealnie w środku procy (długość 0),
        # zwracamy lewą stronę
        if direction.length() == 0:
            return self._object_rect.midleft

        # Normalizacja: Skracamy wektor do długości 1, zachowując kierunek
        direction = direction.normalize()

        # Mnożymy przez promień ptaka
        # Dzięki temu wektor sięga od środka idealnie do krawędzi
        anchor_vector = projectile_center - (direction * self._radius)

        return (anchor_vector.x, anchor_vector.y)
