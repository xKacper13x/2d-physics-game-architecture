from entities.objects_base import PhysicalObject
import pygame
import pymunk


class Projectile(PhysicalObject):
    """
    Represents a projectile fired from the slingshot.

    This class orchestrates the projectile's lifecycle, including:
    - Interactive dragging and slingshot tension (mouse input).
    - Physics state transitions (Static to Dynamic).
    - Flight logic and slingshot band detachment detection.
    - Dynamic calculation of visual anchor points for the rubber band.

    Attributes:
        _pull_vector (pygame.Vector2): The vector representing the tension
                                       direction.
                                       Used to detect when the projectile
                                       passes the slingshot center.
        _start_pos (tuple): The origin point (slingshot center) for resets.
        _shape (pymunk.Poly): The circular collision hitbox.
    """
    def __init__(self, space: pymunk.Space,
                 object_data: dict, slingshot_pos: tuple):
        """
        Initializes the projectile at the slingshot starting position.

        Args:
            space (pymunk.Space): The physical simulation space.
            object_data (dict): Configuration data (mass, score, etc.).
            slingshot_pos (tuple): The (x, y) coordinates of the
                                   slingshot center.
        """
        self._mass = object_data['mass']

        self._pos = slingshot_pos
        super().__init__(space, object_data, self._pos)
        self._score = object_data['score']
        self._pull_vector = pygame.Vector2(0, 0)
        self._start_vec = pygame.math.Vector2(self._pos)

        self._create_physics(space)

    def _create_physics(self, space: pymunk.Space) -> None:
        """
        Initializes the projectile at the slingshot starting position.

        Args:
            space (pymunk.Space): The physical simulation space.
            object_data (dict): Configuration data (mass, score, etc.).
            slingshot_pos (tuple): The (x, y) coordinates of the
                                    slingshot center.
        """
        # Set a high moment of inertia for initial stability
        HIGH_MOMENT_INERTIA = 999990
        self._moment = HIGH_MOMENT_INERTIA

        # Initialize as Static to bypass gravity during the aiming phase
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.STATIC)
        self._body.position = self._pos
        self._shape = pymunk.Circle(self._body, self._radius)

        self._shape.friction = 1.0
        self._shape.elasticity = 0.7
        self._shape.game_object = self

        space.add(self._body, self._shape)

    def launch(self, impulse_vector: tuple) -> None:
        """
        Transitions the projectile to a dynamic state and applies an impulse.

        Args:
            impulse_vector (tuple): The (x, y) force vector for the launch.
        """
        self._body.body_type = pymunk.Body.DYNAMIC
        self._body.mass = self._mass
        self._body.moment = self._moment

        self._body.apply_impulse_at_local_point(impulse_vector)
        start_vec = pygame.math.Vector2(self._pos)
        current_vec = pygame.math.Vector2(self.position)

        self._pull_vector = current_vec - start_vec

    def go_to_start_pos(self) -> None:
        """Resets the projectile position to the slingshot center(on cancel)"""
        self._body.position = self._pos

    def is_dragged(self, lmb_pressed: bool,
                   mouse_pos: tuple) -> bool:
        """
        Checks if the projectile is currently being manipulated by the user.

        Args:
            lmb_pressed (bool): State of the Left Mouse Button.
            mouse_pos (tuple): Current (x, y) cursor position.

        Returns:
            bool: True if the mouse is hovering over
                    the projectile while pressed.
        """
        if lmb_pressed:
            m_collision = self._object_rect.collidepoint(mouse_pos)
            if m_collision and self._body.body_type == pymunk.Body.STATIC:
                return True
        return False

    def is_on_sling(self, max_distance: int) -> bool:
        """
        Determines if the projectile is still logically
        attached to the sling bands.

        Uses the DOT PRODUCT between the pull vector
        and the current displacement vector.
        If the result is negative, the projectile has passed the
        slingshot's focal point.

        Args:
            max_distance (int): The maximum physical stretch
                                of the rubber bands.

        Returns:
            bool: True if the projectile is still
                  behind or at the slingshot center.
        """
        if self._body.body_type != pymunk.Body.DYNAMIC:
            return True

        slingshot_center = pygame.math.Vector2(self._pos)
        current_pos = pygame.math.Vector2(self.position)
        current_vector = current_pos - slingshot_center

        # Mathematical check for relative direction
        dot_product = current_vector.dot(self._pull_vector)
        if dot_product > 0 and current_vector.length() <= max_distance:
            return True
        else:
            return False

    def _get_mouse_vector(self, slingshot_pos: tuple,
                          mouse_pos: tuple) -> pygame.Vector2:
        """
        Calculates a displacement vector from the slingshot to the mouse.

        Args:
            slingshot_pos (tuple): Origin point.
            mouse_pos (tuple): Target point.

        Returns:
            pygame.Vector2: A vector representing distance
                            and direction to the mouse.
        """
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        sling_x = slingshot_pos[0]
        sling_y = slingshot_pos[1]

        vector = pygame.Vector2(mouse_x - sling_x, mouse_y - sling_y)
        return vector

    def drag(self, slingshot_pos: tuple, mouse_pos: tuple,
             max_distance: int) -> None:
        """
        Moves the projectile according to mouse input,
        clamped by slingshot range.

        Args:
            slingshot_pos (tuple): The center point of the slingshot.
            mouse_pos (tuple): The current world coordinates of the mouse.
            max_distance (int): The maximum allowable tension length.
        """
        vector = self._get_mouse_vector(slingshot_pos, mouse_pos)
        if vector.length() > max_distance:
            vector.scale_to_length(max_distance)

        new_pos = pygame.Vector2(slingshot_pos) + vector
        self._body.position = tuple(new_pos)

    @property
    def body(self) -> pymunk.Body:
        """Returns physical body."""
        return self._body

    @property
    def shape(self):
        """Returns object's hitbox."""
        return self._shape

    @property
    def rubber_anchor(self) -> tuple:
        """
        Calculates the exact edge point for the rubber band attachment.

        Uses vector normalization to find the outer boundary of the projectile
        relative to the slingshot center.

        Returns:
            tuple: (x, y) coordinates of the visual anchor
                    on the object's surface.
        """
        projectile_center = pygame.math.Vector2(self.position)
        slingshot_center = self._start_vec

        direction = slingshot_center - projectile_center

        # Fallback for zero-length vector to prevent division by zero
        if direction.length() == 0:
            return self._object_rect.midleft

        direction = direction.normalize()
        # Scale the unit vector by radius to reach the edge
        anchor_vector = projectile_center - (direction * self._radius)

        return (anchor_vector.x, anchor_vector.y)
