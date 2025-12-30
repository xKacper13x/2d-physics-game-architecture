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

    def update(self):
        pos_x = int(self._body.position.x)
        pos_y = int(self._body.position.y)
        self._object_rect.center = (pos_x, pos_y)

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
        self._rubber_width = object_data['rubber_width']
        self._img_path = object_data['img_path']

        self._left_fork_offset = pygame.math.Vector2(self._width / -4.15,
                                                     self._height / -3)
        self._right_fork_offset = pygame.math.Vector2(self._width / 4.15,
                                                      self._height / -2.6)

        super().__init__(self._pos, self._size, self._img_path)

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

    def draw(self, screen):
        screen.blit(self._image, self._object_rect)


class Structure(GameObject):
    def __init__(self, space, object_data):
        self._name = object_data['name']
        self._mass = object_data['mass']
        self._width = object_data['width']
        self._height = object_data['height']
        self._size = (self._width, self._height)

        position = (object_data['pos_x'], object_data['pos_y'])
        self._starting_pos = position

        self._img_path = object_data['img_path']
        self._create_physics(space)
        super().__init__(self._starting_pos, self._size, self._img_path)

    def _create_physics(self, space):
        # oblicza moment bezwladności
        self._moment = pymunk.moment_for_box(self._mass, self._size)
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.DYNAMIC)
        self._body.position = self._starting_pos
        self._shape = pymunk.Poly.create_box(self._body, self._size)
        self._shape.friction = 0.5
        self._shape.elasticity = 0.1
        space.add(self._body, self._shape)

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


class Projectile(GameObject):
    def __init__(self, space, object_data, position):
        self._name = object_data['name']
        self._mass = object_data['mass']
        self._radius = object_data['radius']
        self._starting_pos = position
        self._img_path = object_data['img_path']

        self._create_physics(space)
        diameter = int(2*self._shape.radius)
        self._size = (diameter, diameter)
        super().__init__(self._starting_pos, self._size, self._img_path)

    def _create_physics(self, space):
        # oblicza moment bezwladności
        self._moment = 999990
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.STATIC)
        self._body.position = self._starting_pos
        self._shape = pymunk.Circle(self._body, self._radius)

        self._shape.friction = 1.0
        self._shape.elasticity = 0.6

        space.add(self._body, self._shape)

    def launch(self, impulse_vector):
        self._body.body_type = pymunk.Body.DYNAMIC
        self._body.mass = self._mass
        self._body.moment = self._moment
        self._launching_position = self.position()

        self._body.apply_impulse_at_local_point(impulse_vector)
        start_vec = pygame.math.Vector2(self._starting_pos)
        current_vec = pygame.math.Vector2(self.position())

        self._pull_vector = current_vec - start_vec

    def go_to_start_pos(self):
        self._body.position = self._starting_pos

    def is_dragged(self) -> bool:
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            m_collision = self._object_rect.collidepoint(mouse_pos)
            if m_collision and self._body.body_type == pymunk.Body.STATIC:
                return True
        return False

    def is_on_sling(self) -> bool:
        if self._body.body_type != pymunk.Body.DYNAMIC:
            return True

        slingshot_center = pygame.math.Vector2(self._starting_pos)
        current_pos = pygame.math.Vector2(self.position())
        current_vector = current_pos - slingshot_center

        # 3. ILOCZYN SKALARNY (Dot Product)
        # Sprawdzamy kąt między "Wektorem Naciągu" a "Aktualnym Wektorem".
        # Jeśli wynik > 0:
        # Pocisk jest nadal po stronie naciągu (Leci do procy).
        # Jeśli wynik < 0:
        # Pocisk minął środek procy i leci w świat (Guma znika).
        dot_product = current_vector.dot(self._pull_vector)
        if dot_product > 0:
            return True
        else:
            return False

    def drag(self, slingshot_pos, max_distance):
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        sling_x = slingshot_pos[0]
        sling_y = slingshot_pos[1]

        vector = pygame.Vector2(mouse_x - sling_x, mouse_y - sling_y)
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
        slingshot_center = pygame.math.Vector2(self._starting_pos)

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

        self._start_point = (-200, self._y_pos)
        self._end_point = (self._width, self._y_pos)
        self._create_physics(space)

    def _create_physics(self, space):
        self._body = space.static_body

        self._shape = pymunk.Segment(self._body, self._start_point,
                                     self._end_point, 5)

        # Właściwości fizyczne
        # Maksymalne tarcie (żeby elementy się nie ślizgały jak na lodzie)
        self._shape.friction = 1.0

        # Mała sprężystość (żeby nie odbijały się jak guma)
        self._shape.elasticity = 0.1

        space.add(self._shape)
