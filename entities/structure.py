from entities.objects_base import PhysicalObject
import pymunk


class Structure(PhysicalObject):
    """
    Represents a destructible structural element (e.g., blocks, crates, beams).

    These entities form the defensive fortifications protecting the enemies.
    They are fully simulated physical objects that can take damage from
    impacts and eventually be destroyed, triggering score rewards.
    """
    def __init__(self, space: pymunk.Space, object_data: dict):
        """
        Initializes the structure component using provided configuration data.

        Args:
            space (pymunk.Space): The physical simulation environment.
            object_data (dict): Dictionary containing physical and
                                visual parameters (mass, health, asset paths).
        """
        super().__init__(space, object_data)
        self._mass = object_data['mass']

        self._img_path = object_data['img_path']
        self._create_physics(space)

    def _create_physics(self, space: pymunk.Space) -> None:
        """
        Registers the structure's rigid body and collision shape within Pymunk.

        Configures:
        - Moment of inertia optimized for rectangular geometry.
        - Dynamic body properties for realistic reaction to impulses.
        - High friction coefficient to ensure structural stability of
          complex builds.

        Args:
            space (pymunk.Space): The simulation space to register the entity.
        """
        # Calculate moment of inertia for a rectangular box
        self._moment = pymunk.moment_for_box(self._mass, self._size)
        self._body = pymunk.Body(self._mass, self._moment, pymunk.Body.DYNAMIC)
        self._body.position = self._pos
        self._shape = pymunk.Poly.create_box(self._body, self._size)

        # Physics tuning:
        # Higher friction prevents components from sliding apart prematurely
        self._shape.friction = 0.5
        # Low elasticity prevents excessive bouncing
        self._shape.elasticity = 0.1
        # Injecting reference for collision handling and spatial queries
        self._shape.game_object = self

        space.add(self._body, self._shape)

    def update(self, screen_size: tuple,
               objects_to_kill: list | None = None) -> list | None:
        """
        Updates the structure's state for the current frame.

        Delegates damage calculation and state synchronization to the
        PhysicalObject base class.

        Args:
            screen_size (tuple): Current logical viewport dimensions.
            objects_to_kill (list | None): Collection of objects
                                           marked for removal.

        Returns:
            list | None: Updated collection of objects flagged for removal.
        """
        if objects_to_kill is None:
            return []
        return super().update(screen_size, objects_to_kill)

    def draw(self, screen):
        """
        Renders the structure sprite.
        Inherits rotation and positioning logic from PhysicalObject.
        """
        super().draw(screen)
