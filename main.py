from states.base_state import State
from states.main_menu_state import MainMenuState
from states.game_state import GameState
from states.pause_state import PauseState
from states.level_complete_state import LevelCompleteState
from core.signals import GameSignal
from core.input_handler import InputHandler
import pygame
import sys
import ctypes


class AngryKnightsApp:
    """
    The primary entry point and lifecycle manager
    for the 'Angry Knights' application.

    This class serves as the application's core controller, responsible for:
    - Initializing the Pygame framework and rendering context.
    - Orchestrating the main execution loop (Game Loop).
    - Managing global events (e.g., display toggles, application shutdown).
    - Implementing the State Machine pattern to handle transitions between
      Menu, Gameplay, and UI states.

    Attributes:
        _screen (pygame.Surface): The primary display surface for rendering.
        _is_fullscreen (bool): A flag indicating the current display mode.
        _screen_size (pygame.Vector2): 2d Vector containing screen's
                                       width and height.
        _clock (pygame.time.Clock): A high-resolution timer
                                    for frame rate control (FPS).
        _running (bool): Control flag for the main execution loop.
        _state (State): The currently active state object (e.g., MainMenu).
    """
    def __init__(self):
        """
        Initializes app, sets window with its size, icon and firts state.
        With lack of icon file, occuring error is ignored in order to keep
        the app running.
        """
        pygame.init()

        try:
            icon_path = 'assets/images/Title_Screen_button.png'
            icon_image = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_image)
        except FileNotFoundError:
            pass

        self._screen = pygame.display.set_mode((1920, 1080), pygame.SCALED)
        self._is_fullscreen = False
        pygame.display.set_caption("Angry Knights")
        self._screen_size = self.screen_size
        self._clock = pygame.time.Clock()
        self._running = True

        self._input_handler = InputHandler()

        self._state = MainMenuState(self._screen_size)

    @property
    def screen_size(self) -> pygame.Vector2:
        """
        Returns current screen size

        Returns:
            pygame.Vector2: Vector containing screens width and height.
        """
        screen_x = self._screen.get_width()
        screen_y = self._screen.get_height()
        return pygame.Vector2(screen_x, screen_y)

    def _change_screen_mode(self) -> None:
        """
        Toggles the display mode between windowed and fullscreen.

        Leverages the pygame.SCALED flag to ensure a consistent 1920x1080
        logical aspect ratio regardless of physical screen resolution.
        """
        if self._is_fullscreen:
            self._screen = pygame.display.set_mode((1920, 1080), pygame.SCALED)
            self._is_fullscreen = False
        else:
            self._screen = pygame.display.set_mode((1920, 1080),
                                                   pygame.FULLSCREEN |
                                                   pygame.SCALED)
            self._is_fullscreen = True

    def _manage_states(self, result: GameSignal) -> State:
        """
        The centralized orchestration hub for the State Machine.

        Interprets signals emitted by the current state and instantiates the
        appropriate new state to drive the application forward.

        Args:
            result (GameSignal): A signal enum representing the
                                 desired state transition.

        Returns:
            State: The new state object for the next frame, or the existing
                   state if no transition is required.
        """
        if result is GameSignal.GO_TO_MENU:
            state = MainMenuState(self._screen_size)

        elif result is GameSignal.START_GAME:
            state = GameState(self._screen_size, 1)

        elif result is GameSignal.PAUSE_GAME:
            state = PauseState(self._screen_size, self._state)

        elif result is GameSignal.UNPAUSE_GAME:
            state = self._state.paused_state

        elif result is GameSignal.END_LEVEL:
            state = LevelCompleteState(self._screen_size, self._state)

        elif result is GameSignal.NEXT_LEVEL:
            current_level = self._state.level
            try:
                next_level_index = current_level + 1
                state = GameState(self._screen_size, next_level_index)
            except FileNotFoundError:
                state = MainMenuState(self._screen_size)

        elif result is GameSignal.RESTART_LEVEL:
            current_level = self._state.level
            state = GameState(self._screen_size, current_level)

        else:
            state = self._state
        return state

    def run(self) -> None:
        """
        Executes the main application loop (The "Heartbeat").

        Continuously processes inputs, updates the active state logic, and
        renders frames while managing delta time for consistent
        physics simulation.
        """
        delta_time = 0.1
        while self._running:
            events = pygame.event.get()

            input_data = self._input_handler.process_data(events)

            if input_data.key_F11_down:
                self._change_screen_mode()

            result = self._state.update(input_data)
            self._state = self._manage_states(result)

            # Rendering
            self._state.draw(self._screen)

            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False

            pygame.display.flip()
            delta_time = self._clock.tick(60) / 1000
            delta_time = max(0.001, min(0.1, delta_time))


if __name__ == '__main__':
    if sys.platform == "win32":
        myappid = 'mojanazwa.gra.knights.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    App = AngryKnightsApp()
    App.run()
