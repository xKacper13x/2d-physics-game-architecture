from dataclasses import dataclass
import pygame


@dataclass
class PhysicsParams:
    """
    Container for physical properties required for trajectory simulation.

    Ensures data integrity and simplifies parameter passing between services.
    """
    mass: int
    gravity: pygame.Vector2
    power: int
    direction: pygame.Vector2

    def __post_init__(self):
        """
        Validates input data after initialization.
        """
        self.mass = max(1, self.mass)


@dataclass
class WorldBounds:
    """
    Defines the spatial constraints and limits for the physics simulation.
    """
    ground_level: int
    screen_center: int
