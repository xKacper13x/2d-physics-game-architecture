from entities.objects_base import GameObject
import pymunk
import pygame


class Slingshot(GameObject):
    """
    Represents the slingshot launcher mechanism.

    This class handles the visual representation of the launcher, including:
    - Rendering the main slingshot sprite.
    - Orchestrating the "Z-order" drawing of rubber bands to encapsulate
      the projectile visually.
    - Managing launch power multipliers used for impulse calculations.

    Attributes:
        _power (int): Force multiplier for projectile launching.
        _rubber_color (tuple): RGB color of the slingshot bands.
        _rubber_width (int): Line thickness for band rendering.
        _left_fork_offset (pygame.Vector2): Calibration offset
                                            for the left fork tip.
        _right_fork_offset (pygame.Vector2): Calibration offset for
                                             the right fork tip.
    """
    def __init__(self, data: dict):
        """
        Initializes the slingshot mechanism using configuration data.

        Args:
            data (dict): Configuration dictionary
                         containing 'slingshot' parameters.
        """
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

    @property
    def power(self) -> int:
        """Return slingshot's force multiplyer."""
        return self._power

    @property
    def height(self) -> int:
        """
        Returns the sprite height, used to clamp the maximum pull distance.
        """
        return self._height

    def draw_outer_rubber(self, screen: pygame.Surface,
                          projectile_pos: tuple | None = None) -> None:
        """
        Renders the rear section of the rubber band.

        If the slingshot is at rest, it draws
        a straight line between both forks.

        Args:
            screen (pygame.Surface): The target rendering surface.
            projectile_pos (tuple | None): The current position of the
                                           projectile's anchor point.
        """
        left_fork = self._pos + self._left_fork_offset
        if projectile_pos is None:
            right_fork = self._pos + self._right_fork_offset
            pygame.draw.line(screen, self._rubber_color, left_fork,
                             right_fork, self._rubber_width)
        else:
            pygame.draw.line(screen, self._rubber_color, left_fork,
                             projectile_pos, self._rubber_width)

    def draw_inner_rubber(self, screen: pygame.Surface,
                          projectile_pos: tuple) -> None:
        """
        Renders the front section of the rubber band.

        Args:
            screen (pygame.Surface): The target rendering surface.
            projectile_pos (tuple): The current position of the projectile's
                                    anchor point.
        """
        right_fork = self._pos + self._right_fork_offset
        pygame.draw.line(screen, self._rubber_color, right_fork,
                         projectile_pos, self._rubber_width)


class Ground:
    """
    Represents the static physical environment boundary (the floor).

    This entity is invisible but provides critical physics constraints,
    preventing objects from falling indefinitely and managing environmental
    friction/elasticity.

    Attributes:
        _y_pos (int): The vertical coordinate of the ground level.
        _body (pymunk.Body): Static physics body associated with the ground.
        _shape (pymunk.Segment): Collision segment defining
                                 the ground boundary.
    """
    def __init__(self, screen_size: pygame.Vector2, y_pos: int,
                 space: pymunk.Space):
        """
        Initializes the physical ground segment.

        Args:
            screen_size (pygame.Vector2): Display dimensions to
                                          calculate width.
            y_pos (int): The vertical (Y) position of the ground.
            space (pymunk.Space): The Pymunk physics space.
        """
        self._width = 3 * screen_size[0]
        self._y_pos = y_pos

        self._start_point = (-350, self._y_pos)
        self._end_point = (self._width, self._y_pos)
        self._create_physics(space)

    @property
    def pos_y(self) -> int:
        """Returns the Y-coordinate of the floor level."""
        return self._y_pos

    def _create_physics(self, space: pymunk.Space) -> None:
        """
        Configures a static collision segment within the physics engine.

        The segment is assigned a high friction coefficient to prevent sliding
        and low elasticity to simulate realistic ground impact.
        """
        self._body = space.static_body

        self._shape = pymunk.Segment(self._body, self._start_point,
                                     self._end_point, 5)

        # Physics Properties:
        # High friction ensures objects don't slide indefinitely
        self._shape.friction = 1.0

        # Low elasticity prevents "trampoline" effects on impact
        self._shape.elasticity = 0.2

        space.add(self._shape)
