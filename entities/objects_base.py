import pygame
import core.helpers as helpers
import math
import pymunk
import exceptions


class GameObject:
    """
    Base class for all visual objects in the game.

    Handles loading images, scaling, and basic positioning on the screen.

    Attributes:
        _name (str): Identifier used for debugging and logging.
        _img_path (str): File path to the image resource.
        _image (pygame.Surface): The actual image used for rendering.
        _object_rect (pygame.Rect): Rectangle for positioning and boundaries.
        _pos (pygame.Vector2): Current center position (x, y).
    """
    def __init__(self, object_data: dict,
                 position: tuple | pygame.Vector2 = None):
        """
        Initializes the object using a configuration dictionary.

        Args:
            object_data (dict): Dictionary containing:
                - 'name': Object identifier.
                - 'img_path': Path to graphic file.
                - 'pos_x', 'pos_y': Initial coordinates.
                - 'height' / 'width' (optional): Dimensions for scaling.
                - 'radius' (optional): Used if the object is circular.
        """
        self._name = object_data.get('name', '')
        self._img_path = object_data.get('img_path', '')

        if 'height' in object_data:
            self._height = int(object_data['height'])
            if 'width' in object_data:
                self._width = int(object_data.get('width', None))
                self._size = (self._width, self._height)
                self._image = self._load_image(self._img_path, self._size)
            else:
                self._image = self._load_image(self._img_path, self._height)
                self._width = self._image.get_width()
                self._size = (self._width, self._height)
        else:
            self._radius = int(object_data.get('radius', 0))
            diameter = int(2*self._radius)
            self._size = (diameter, diameter)
            try:
                helpers.check_size(self._size)
            except exceptions.InvalidConfigurationError:
                self._size = None

            self._image = self._load_image(self._img_path, self._size)

        self._object_rect = self._image.get_rect()
        if position is not None:
            self._pos = position
        else:
            self._pos = (object_data.get('pos_x', 0),
                         object_data.get('pos_y', 0))
        self._object_rect.center = self._pos

    @property
    def name(self) -> str:
        """Returns object's name"""
        return self._name

    @property
    def position(self) -> pygame.Vector2:
        """Returns current position of object's center"""
        return pygame.Vector2(self._object_rect.center)

    def _load_image(self, img_path: str,
                    img_size: int | float | tuple |
                    pygame.Vector2 | None = None) -> None:
        """Helper for safe image loading via helpers module."""
        return helpers.load_image(img_path, img_size)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws objects on the provided Surface.

        Args:
            screen (pygame.Surface): Target screen to draw on.
        """
        screen.blit(self._image, self._object_rect)

    def update(self, objects_to_kill: list = None):
        """Metoda do nadpisania w klasach pochodnych."""
        pass


class PhysicalObject(GameObject):
    """
    Extends GameObjects with physics properties using Pymunk.

    Manages:
    - Mass, health, and collision damage detection.
    - Synchronizing visual position with the physics body.
    - Rotating graphics based on physics body angle.
    - Scoring system for damaging or destroying the object.

    Attributes:
        _space (pymunk.Space): A physical space, to which object belongs.
        _mass (float): Object's mass.
        _health (float): Health points.
        _score (int): Points for destroing this objects.
        _body (pymunk.Body): Physical body.
        (Must be assigned in the inheriting class).
        _last_angle (float): The angle by which the object was rotated
                             in the previous frame.
        _pos (tuple): Object's position on the screen.
    """
    def __init__(self, space: pymunk.Space, object_data: dict,
                 position: tuple | pygame.Vector2 = None):
        """
        Initializes the physical object and its properties

        Args:
            space (pymunk.Space): The Pymunk physics space.
            object_data (dict): Configuration (mass, health, image data).
        """
        self._space = space
        self._mass = object_data.get('mass', 1)
        self._mass = max(self._mass, 1)
        self._last_angle = 0.0

        super().__init__(object_data, position)

        self._health = object_data.get('health', 100)
        if self._health == 'inf':
            self._health = math.inf

        self._score = 0
        self._max_x = self._pos[0] + 100
        self._original_image = self._image

        self._last_velocity = pygame.Vector2(0, 0)

    @property
    def mass(self) -> int:
        """Return the object's mass."""
        return self._mass

    def collect_points(self) -> int:
        """
        Return points collected by the object(for damaging/ destroing it)
        and resets points counter

        Returns:
            int: Total points to add to the player's score.
        """
        points = self._score
        self._score = 0
        return points

    def _take_damage(self, damage: int) -> None:
        """
        Reduces health and adds points based on damage taken.

        Args:
            damage (float): The amount of damage (impact force).
        """
        new_health = self._health - abs(damage)
        self._score += int(abs(damage) * 3)
        self._health = max(new_health, 0)

    def off_screen(self, screen_size: pygame.Vector2) -> bool:
        """
        Checks if objects is out of the boundaries

        Args:
            screen_size (pygame.Vector2 | tuple): Dimensions of
                                                  the game window.

        Returns:
            bool: True if the object is far outside the visible area.
        """
        max_x = screen_size[0]
        off_screen = False
        if self._body.position.x > max_x + 150 or self._body.position.x < -150:
            off_screen = True

        return off_screen

    @property
    def velocity(self) -> pymunk.Vec2d:
        """Returns the current velocity vector from Pymunk"""
        return self._body.velocity

    def update(self, screen_size: tuple,
               objects_to_kill: list | None = None) -> list | None:
        """
        Updates the object's state for current frame.

        - Syncs sprite position with physics body.
        - Calculates impact force based on velocity changes.
        - Deals damage for collisions above a certain threshold.
        - Adds to 'objects_to_kill' if health reaches zero.

        Args:
            objects_to_kill (list | None): List of objects marked for removal.

        Returns:
            list | None: Updated list of objects to destroy.
        """
        pos_x = int(self._body.position.x)
        pos_y = int(self._body.position.y)
        self._object_rect.center = (pos_x, pos_y)
        if objects_to_kill is None:
            return []
        if self in objects_to_kill:
            return objects_to_kill

        current_velocity = self._body.velocity
        impact_velocity = current_velocity - self._last_velocity
        self._last_velocity = pygame.Vector2(current_velocity.x,
                                             current_velocity.y)

        impact_force = impact_velocity.length
        DAMAGE_THRESHOLD = 100

        if impact_force > DAMAGE_THRESHOLD:
            damage_to_deal = impact_force * 0.3
            self._take_damage(damage_to_deal)

        if self.off_screen(screen_size):
            self._health = 0
            self._score += 700

        if self._health <= 0:
            objects_to_kill.append(self)
        return objects_to_kill

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws objects on the provided Surface.

        Args:
            screen (pygame.Surface): Target screen to draw on.
        """
        angle = self._body.angle
        angle = -1 * math.degrees(angle)

        # Rotation optimization: Updates the sprite only when
        #   the angular change is significant.
        if abs(angle - self._last_angle) > 1.0:
            self._image = pygame.transform.rotate(self._original_image, angle)
            self._last_angle = angle

        # Re-center rect after rotation to prevent sprite drifting
        pos = self._body.position
        self._object_rect = self._image.get_rect(center=(pos.x, pos.y))

        super().draw(screen)
        self._max_x = screen.get_width()
