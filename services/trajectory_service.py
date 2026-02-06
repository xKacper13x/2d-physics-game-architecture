from core.physics_data import PhysicsParams, WorldBounds
import pygame


class TrajectoryService:
    """
    A stateless utility service for projectile motion calculations.

    Decouples the physics simulation from the rendering loop to ensure
    Single Responsibility Principle (SRP) and high testability.
    """
    @staticmethod
    def get_trajectory_points(start_pos: pygame.Vector2,
                              physics: PhysicsParams,
                              bounds: WorldBounds) -> list:
        """
        Calculates a list of predicted coordinates for the
        projectile's flight path.

        The simulation uses the standard kinematic equation for position:
        s = s_0 + v_0t + 0.5at^2
        to accurately predict the parabolic arc based on impulse and gravity.

        Args:
            start_pos (pygame.Vector2): The initial launching position
                                        of the projectile.
            physics (PhysicsParams): Physical properties
                                     (mass, gravity, impulse).
            bounds (WorldBounds): Simulation boundaries
                                  (ground and screen limits).

        Returns:
            list: A list of tuples containing (index, pygame.Vector2)
                  for each point in the arc.
        """
        points = []
        impulse = physics.direction * physics.power
        velocity = impulse / physics.mass
        curr_pos = start_pos
        time_step = 0.12
        i = 1

        x_middle = bounds.screen_center
        ground_y = bounds.ground_level
        gravity = physics.gravity
        while curr_pos.y <= ground_y and curr_pos.x <= x_middle:
            t = i * time_step + time_step
            i += 1

            # s = s0 + vt + 0.5at^2
            curr_pos = start_pos + (velocity * t) + (0.5 * gravity * t * t)
            points.append((i, curr_pos))
        return points
