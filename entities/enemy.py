from entities.objects_base import PhysicalObject
from entities.projectile import Projectile
import pymunk


class Enemy(PhysicalObject):
    """
    Represents an enemy entity within the game world.

    Inherits from PhysicalObject to leverage physics simulation, health
    management, and sprite rendering. This class implements specific
    vulnerability logic, such as instantaneous termination upon contact
    with player-fired projectiles.

    Attributes:
        _pos (tuple): Initial spatial coordinates.
        _moment (float): Moment of inertia for the physics body.
        _body (pymunk.Body): The dynamic physical body simulated by Pymunk.
        _shape (pymunk.shapes.Poly): The collision hitbox for the entity.
        _health (int): Remaining durability of the enemy.
        _score (int): Accumulated points gained from damaging this entity.
    """
    def __init__(self, space: pymunk.Space, object_data: dict):
        """
        Initializes base properties and registers physics
        components within the simulation space.

        Args:
            space (pymunk.Space): The physical simulation environment.
            object_data (dict): Configuration dictionary containing
                               spatial and physical parameters.
        """
        super().__init__(space, object_data)

        self._create_physics(space)

    def _create_physics(self, space: pymunk.Space) -> None:
        """
        Configures and registers the physical presence of the enemy in Pymunk.

        This method defines:
        - Moment of inertia optimized for rectangular bodies.
        - Dynamic body properties for real-time interaction.
        - A slightly narrowed collision shape for improved visual-to-physical
          alignment (hitbox optimization).
        - Material properties including friction and elasticity.
        - Spatial index references (game_object) for efficient collision
          detection and resolution.

        Args:
            space (pymunk.Space): The simulation space to add
                                  the body and shape to.
        """
        self._moment = pymunk.moment_for_box(self._mass, self._size)
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.DYNAMIC)
        self._body.position = self._pos

        # Hitbox optimization: 80% width for better player experience
        self._shape = pymunk.Poly.create_box(self._body, (self._width * 0.8,
                                                          self._height))
        self._shape.friction = 0.5
        self._shape.elasticity = 0.1
        space.add(self._body, self._shape)

    def update(self, screen_size: tuple,
               objects_to_kill: list | None = None) -> list | None:
        """
        Performs the frame-by-frame update logic for the enemy entity.

        Utilizes a spatial shape query to detect high-priority collisions.
        Specifically, implements instant-death logic when interacting with
        Projectile instances, bypassing standard durability calculations
        to reward player accuracy.

        Args:
            screen_size (tuple): Current logical dimensions of the viewport.
            objects_to_kill (list | None): Collection of objects flagged for
                                           removal in the current frame.

        Returns:
            list | None: Updated collection of entities marked for disposal.

        Raises:
            ValueError: If the required 'objects_to_kill' list is not provided,
                        ensuring operational excellence through strict
                        API contracts.
        """
        if objects_to_kill is None:
            raise ValueError('update() method requires objects_to_kill_list')

        contacts = self._space.shape_query(self._shape)
        for contact in contacts:
            other_shape = contact.shape
            if hasattr(other_shape, 'game_object'):
                who_hit_me = other_shape.game_object

                if isinstance(who_hit_me, Projectile):
                    self._health = 0
                    self._score += 1000

        return super().update(screen_size, objects_to_kill)
