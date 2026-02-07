from .base_state import State
from entities.objects_base import PhysicalObject
from entities.static_objects import Slingshot, Ground
from entities.enemy import Enemy
from entities.projectile import Projectile
from entities.structure import Structure
from services.level_service import LevelService
from core.signals import GameSignal
from services.trajectory_service import TrajectoryService
from core.physics_data import PhysicsParams, WorldBounds
from core.input_handler import InputData
import pygame
import pymunk


class GameState(State):
    """
    Manages the active gameplay state for individual levels.

    This controller orchestrates the core game loop, including:
    - Physics simulation lifecycle (initialization, updates, and cleanup).
    - Entity management for projectiles, enemies, and structures.
    - Input processing for the slingshot mechanics
      (aiming, dragging, launching).
    - Level progression logic and score synchronization

    Attributes:
        _ammo_pointer (int): Index tracking the currently active projectile.
        _level (int): Current level's ID.
        _level_service (LevelService): Handles data-driven level loading
                                        and high scores.
        _trajectory_service (TrajectoryService): Predicts
                                                 and renders the flight path.
        _space (pymunk.Space): The physical world simulation container.
        _high_score (int): Current level's points record,
                            stored in game's configuration file.
        _current_score (int): Current amount of points.
        _max_dis (int): Maximum allowable stretch distance
                        for the slingshot bands.
        _projectile_stopped (bool): Flag indicating whether the projectile
                                    stopped moving.
        _timer (float): High-precision accumulator for managing
                        logic delays and transitions.
        _wait_time (int): The predefined latency period (in seconds)
                          before the state transition occurs.
        _ground (Ground): Static ground's object.
        _enemies (list): A registry of currently alive enemies.
        _object_on_sling (Projectile): The projectile currently
                                        loaded in the slingshot.
        _dragged_object (Projectile): The projectile currently
                                        manipulated by the cursor.
        _level_ended (bool): Flag indicating the win/loss
                             state has been triggered.
        _structures (list): A registry of physical structures
                            in the current level.
        _slingshot (Slingshot): Instance of Slingshot
    """
    def __init__(self, screen_size: pygame.Vector2, level: int):
        """
        Initializes the game level, physics space, and UI components.

        Args:
            screen_size (pygame.Vector2): Dimensions of the game window.
            level (int): Numeric ID of the level to be loaded.

        Raises:
            ValueError: If the 'level' argument is not an integer.
        """
        if not isinstance(level, int):
            raise ValueError('Level must be an integer')
        self._ammo_pointer = 0
        self._level = level
        self._space = pymunk.Space()

        self._trajectory_service = TrajectoryService()
        self._level_service = LevelService('objects_config_files')
        data = self._level_service.load_data(f'level{level}.json')
        self._space.gravity = self._level_service.physics_config
        self._high_score = self._level_service.high_score

        super().__init__(screen_size, data)
        background_img_path = data["background_img"]
        self._set_background(background_img_path)
        self._create_buttons()

        self._current_score = 0
        self._update_score_labels(self._current_score, self._high_score)

        self._max_dis = int(self._slingshot.height * 0.8)
        self._object_on_sling = self._current_projectile
        self._dragged_object = None

        self._projectile_stopped = False
        self._level_ended = False
        self._timer = 0
        self._wait_time = 2

        self._ground = Ground(self._screen_size, 940, self._space)

    @property
    def level(self) -> int:
        """Returns the current level number."""
        return self._level

    @property
    def current_score(self) -> int:
        """Returns the current session's accumulated points."""
        return self._current_score

    @property
    def high_score(self) -> int:
        """Returns the historical high score for the level."""
        return self._high_score

    @property
    def scores(self) -> tuple:
        """
        Returns the scoring state as a tuple.

        Returns:
            tuple: (current_score, high_score).
        """
        return (self._current_score, self._high_score)

    def _create_buttons(self) -> None:
        """
        Maps generic button reference from the registry to specific
        class attribute.
        """
        self._pause_button = self._buttons_dict['pause_button']

    def _initialize_objects(self, data: dict) -> list:
        """
        Parses level metadata to instantiate game entities.

        Args:
            data (dict): Full configuration dictionary.

        Returns:
            list: Flattened list of all objects to be rendered and updated.
        """
        objects = super()._initialize_objects(data)
        data = data['objects']

        self._slingshot = Slingshot(data)
        pos = self._slingshot.position
        self._slingshot_pos = (pos[0], pos[1] - 95)

        self._projectiles_data = data['projectiles']
        self._current_projectile = self._initialize_projectile()
        objects.append(self._current_projectile)

        self._enemies = [Enemy(self._space, enemy_data)
                         for enemy_data in data['enemies']]
        self._structures = [Structure(self._space, structure_data)
                            for structure_data in data['structures']]
        return objects + self._enemies + self._structures

    def _initialize_projectile(self) -> Projectile:
        """
        Creates a new projectile instance based on the current ammo pointer.

        Returns:
            Projectile: The instantiated projectile ready for the slingshot.
        """
        data = self._projectiles_data[self._ammo_pointer]
        projectile = Projectile(self._space, data, self._slingshot_pos)
        return projectile

    def _perform_launch(self) -> None:
        """
        Calculates the propulsion vector and triggers the projectile launch.
        Resets the projectile if the pull distance
        is below the minimum threshold.
        """
        start_pos = self._current_projectile.position
        pull_vector = self._slingshot_pos - start_pos

        distance = pull_vector.length()
        MIN_DIS = 70

        if distance >= MIN_DIS:
            power = self._slingshot.power
            self._current_projectile.launch((pull_vector.x*power,
                                             pull_vector.y*power))
        else:
            self._current_projectile.go_to_start_pos()

    def _check_for_launch(self, lmb_released: bool, lmb_pressed: bool,
                          mouse_pos: tuple) -> None:
        """
        Handles mouse interaction logic for aiming and firing the slingshot.

        Args:
            lmb_released (bool): True if the Left Mouse Button
                                 was just released.
            lmb_pressed (bool): True if the Left Mouse Button
                                is currently held.
            mouse_pos (tuple): Current (x, y) coordinates of the mouse cursor.
        """
        if lmb_released:
            if self._dragged_object is not None:
                self._perform_launch()
                self._dragged_object = None

        is_ammo_dragged = self._current_projectile.is_dragged(lmb_pressed,
                                                              mouse_pos)
        if is_ammo_dragged or self._dragged_object is not None:
            self._dragged_object = self._current_projectile
            self._dragged_object.drag(self._slingshot_pos,
                                      mouse_pos,
                                      self._max_dis)
        elif lmb_pressed:
            self._dragged_object = None

    def _kill_object(self, obj_to_remove: PhysicalObject) -> None:
        """
        Safely removes an entity from the physics space and the render list.

        Args:
            obj_to_remove (PhysicalObject): The object instance
                                            to be destroyed.
        """
        space_bodies = self._space.bodies
        if obj_to_remove._body in space_bodies:
            self._space.remove(obj_to_remove._body, obj_to_remove._shape)
        if obj_to_remove in self._objects:
            self._objects.remove(obj_to_remove)
        if isinstance(obj_to_remove, Enemy):
            self._enemies.remove(obj_to_remove)

    def _end_level(self) -> None:
        """
        Initiates the end-of-level sequence.
        Resets score if enemies remain, and triggers the transition timer.
        """
        if self._enemies:
            self._current_score = 0
        self._timer = 0
        self._level_ended = True

    def _draw_trajectory(self, screen: pygame.Surface):
        """
        Calculates and renders a predicted flight path for the projectile.

        Args:
            screen (pygame.Surface): Target rendering surface.
        """
        if self._dragged_object is None:
            return

        sling_pos = pygame.Vector2(self._slingshot_pos)
        start_pos = pygame.Vector2(self._current_projectile.position)
        diff = sling_pos - start_pos
        power = self._slingshot.power

        mass = self._current_projectile.mass
        gravity = pygame.Vector2(self._space.gravity)

        x_middle = self._screen_size[0] / 2
        ground_y = self._ground.pos_y

        physics_params = PhysicsParams(mass, gravity, power, diff)
        world_bounds = WorldBounds(ground_y, x_middle)
        points = self._trajectory_service.get_trajectory_points(start_pos,
                                                                physics_params,
                                                                world_bounds)

        for index, point in points:
            radius = 5 - (index // 10)
            radius = max(radius, 2)
            pygame.draw.circle(screen, (255, 255, 255), point, radius)
            pygame.draw.circle(screen, (0, 0, 0), point, radius, 1)

    def _draw_objects(self, screen: pygame.Surface):
        """
        Renders game entities with specific Z-order for slingshot layers.

        Args:
            screen (pygame.Surface): Target rendering surface.
        """
        if self._object_on_sling is not None:
            rubber_anchor = self._object_on_sling.rubber_anchor
            self._slingshot.draw_inner_rubber(screen,
                                              rubber_anchor)
            super()._draw_objects(screen)
            self._slingshot.draw_outer_rubber(screen,
                                              rubber_anchor)
        else:
            self._slingshot.draw_outer_rubber(screen)
            super()._draw_objects(screen)

    def _update_entities(self) -> None:
        """
        Updates physics-driven entities, collects points,
        and cleans up destroyed objects.
        """
        objects_to_kill = []
        for obj in self._objects:
            if isinstance(obj, (Enemy, Structure)):
                objects_to_kill = obj.update(self._screen_size,
                                             objects_to_kill)
                self._current_score += obj.collect_points()
                self._update_score_labels(self._current_score,
                                          self._high_score)
            else:
                obj.update(self._screen_size)

        for obj in objects_to_kill:
            self._kill_object(obj)

    def _update_slingshot_status(self) -> None:
        """
        Verifies if the projectile is physically seated on the slingshot bands.
        """
        if self._current_projectile.is_on_sling(self._max_dis):
            self._object_on_sling = self._current_projectile
        else:
            self._object_on_sling = None

    def _update_projectile_status(self) -> None:
        """
        Monitors the projectile post-launch
        to detect when it stops or exits bounds.
        """
        if self._current_projectile.is_on_sling(self._max_dis):
            return

        if not self._projectile_stopped:
            velocity = pygame.Vector2(
                            self._current_projectile.velocity).length()

            is_stopped = velocity < 4
            is_off_screen = self._current_projectile.off_screen(
                                                            self._screen_size)

            if is_stopped or is_off_screen:
                self._projectile_stopped = True

                self._timer = 0

    def _handle_input(self, input_data: InputData) -> str:
        """
        Evaluates input data to detect pause requests.

        Checks interaction with the on-screen Pause button and the
        standard ESC hotkey to trigger state interruption.

        Args:
            input_data (InputData): The standardized input snapshot for
                                    the current frame.

        Returns:
            str: A GameSignal command (e.g., PAUSE_GAME) indicating
                 the desired state transition.
        """
        result = GameSignal.STAY
        if self._pause_button.is_clicked(input_data.lmb_clicked,
                                         input_data.mouse_pos):
            result = GameSignal.PAUSE_GAME

        if input_data.key_esc_down:
            result = GameSignal.PAUSE_GAME
        return result

    def _handle_projectile_transition(self) -> None:
        """
        Handles the lifecycle of projectiles after they have come to a rest.

        Increments a timer once a projectile stops moving. After a defined
        delay, it either spawns the next projectile in the queue or
        triggers the end of the level if ammunition is depleted.
        """
        if self._projectile_stopped:
            self._timer += 1/60
            if self._timer >= 2:
                self._ammo_pointer += 1
                self._kill_object(self._current_projectile)

                if self._ammo_pointer >= len(self._projectiles_data):
                    if not self._level_ended:
                        self._end_level()
                else:
                    self._current_projectile = self._initialize_projectile()
                    self._objects.append(self._current_projectile)
                    self._projectile_stopped = False
                    self._timer = 0

    def update(self, input_data: InputData) -> str:
        """
        Main logic step. Synchronizes physics simulation and game rules.

        Args:
            input_data (InputData): Object containing
                                    current frame input states.

        Returns:
            str: GameSignal command for state management.
        """
        self._space.step(1/60)

        if not self._level_ended:
            self._check_for_launch(input_data.lmb_released,
                                   input_data.lmb_pressed,
                                   input_data.mouse_pos)

        self._update_slingshot_status()

        self._update_entities()

        self._update_projectile_status()

        if not self._enemies and not self._level_ended:
            self._end_level()

        self._handle_projectile_transition()

        next_state = self._handle_input(input_data)

        if self._level_ended:
            self._timer += 1/60
            if self._timer >= self._wait_time:
                self._level_service.save_new_high_score(self._level,
                                                        self._current_score)
                next_state = GameSignal.END_LEVEL
        return next_state

    def draw(self, screen: pygame. Surface) -> None:
        """
        Main rendering call. Orchestrates background,
        trajectory, and entity drawing.

        Args:
            screen (pygame.Surface): The primary display surface.
        """
        super().draw(screen)
        self._draw_trajectory(screen)
        self._slingshot.draw(screen)
