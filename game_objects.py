import helpers
import pymunk
import pygame
import math


class GameObject:
    def __init__(self, object_data: dict) -> None:
        self._name = object_data['name']
        self._img_path = object_data['img_path']

        if 'height' in object_data.keys():
            self._height = int(object_data['height'])
            self._image = self.load_image(self._img_path, self._height)
            self._width = self._image.get_width()
            self._size = (self._width, self._height)
        else:
            self._radius = int(object_data['radius'])
            diameter = int(2*self._radius)
            self._size = (diameter, diameter)

            helpers.check_size(self._size)
            self._image = self.load_image(self._img_path, self._size)

        self._object_rect = self._image.get_rect()
        self._object_rect.center = self._pos

    def name(self) -> str:
        return self._name

    def position(self):
        return self._object_rect.center

    def load_image(self, img_path, img_size=None):
        return helpers.load_image(img_path, img_size)

    def update(self, objects_to_kill: list = None) -> None:
        pos_x = int(self._body.position.x)
        pos_y = int(self._body.position.y)
        self._object_rect.center = (pos_x, pos_y)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._image, self._object_rect)


class Slingshot(GameObject):
    def __init__(self, data):
        object_data = data['slingshot']
        self._pos = (object_data['pos_x'], object_data['pos_y'])
        super().__init__(object_data)

        self._rubber_color = (object_data['color_R'], object_data['color_G'],
                              object_data['color_B'])
        self._rubber_width = object_data['rubber_width']

        self._left_fork_offset = pygame.math.Vector2(self._width / -4.15,
                                                     self._height / -3)
        self._right_fork_offset = pygame.math.Vector2(self._width / 4.15,
                                                      self._height / -2.6)

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
        super().update()
        if objects_to_kill is None:
            return None
        if self in objects_to_kill:
            return objects_to_kill

        current_velocity = self._body.velocity
        impact_velocity = current_velocity - self._last_velocity
        self._last_velocity = pygame.Vector2(current_velocity.x,
                                             current_velocity.y)

        impact_force = impact_velocity.length
        DAMAGE_THRESHOLD = 20

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

    def get_rubber_anchor(self):
        projectile_center = pygame.math.Vector2(self.position())
        slingshot_center = pygame.math.Vector2(self._pos)

        # Obliczamy wektor kierunku: Od Ptaka -> Do Procy
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

        # Zwracamy jako krotkę (x, y)
        return (anchor_vector.x, anchor_vector.y)


class Ground:
    def __init__(self, screen_size: pygame.Vector2, y_pos: int, space) -> None:
        self._width = 3 * screen_size[0]
        self._y_pos = y_pos

        self._start_point = (-350, self._y_pos)
        self._end_point = (self._width, self._y_pos)
        self._create_physics(space)

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
