from .base_state import State
from core.signals import GameSignal
from core.input_handler import InputData
from services.base_service import BaseService
import pygame


class PauseState(State):
    """
    Manages the 'Pause Menu' overlay interaction.

    This state implements a non-destructive suspension of the active gameplay.
    It renders on top of the preserved game state (Overlay pattern), allowing
    the player to resume, restart, or exit without losing the visual context.

    Attributes:
        _paused_state (State): The suspended GameState instance, retained in
                                memory for resumption or background rendering.
        _play_button (Button): UI control to resume execution.
        _retry_button (Button): UI control to reload the current level.
        _settings_button (Button): UI control for configuration (placeholder).
        _quit_button (Button): UI control to return to the main menu.
    """
    def __init__(self, screen_size: pygame.Vector2, paused_state: State):
        """
        Initializes the pause overlay and captures the current game context.

        Args:
            screen_size (pygame.Vector2): Dimensions of the application window.
            paused_state (State): The active GameState to be suspended.
        """
        self._paused_state = paused_state
        service = BaseService()
        data = service.load_data('pause.json')
        super().__init__(screen_size, data)
        self._create_buttons()

    @property
    def paused_state(self) -> State:
        """Returns the suspended game state instance."""
        return self._paused_state

    @property
    def level(self) -> int:
        """Returns the level ID from the suspended state context."""
        return self._paused_state.level

    def _create_buttons(self) -> None:
        """
        Maps UI components from the generic registry
        to class attributes.
        """
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._settings_button = self._buttons_dict['settings_button']
        self._quit_button = self._buttons_dict['quit_button']

    def _handle_input(self, input_data: InputData) -> GameSignal:
        """
        Processes user interaction with the pause menu controls.

        Evaluates button clicks (Resume, Retry, Quit) and hotkeys (ESC)
        to determine the next state transition.

        Args:
            input_data (InputData): Snapshot of current frame inputs
                                    (mouse state, position, keyboard).

        Returns:
            GameSignal: Command indicating the desired state transition
                        (e.g., UNPAUSE_GAME, RESTART_LEVEL).
        """
        next_state = GameSignal.STAY
        if self._play_button.is_clicked(input_data.lmb_clicked,
                                        input_data.mouse_pos):
            return GameSignal.UNPAUSE_GAME
        if self._retry_button.is_clicked(input_data.lmb_clicked,
                                         input_data.mouse_pos):
            return GameSignal.RESTART_LEVEL
        if self._settings_button.is_clicked(input_data.lmb_clicked,
                                            input_data.mouse_pos):
            # Placeholder for future settings implementation
            pass
        if self._quit_button.is_clicked(input_data.lmb_clicked,
                                        input_data.mouse_pos):
            return GameSignal.GO_TO_MENU

        if input_data.key_esc_down:
            next_state = GameSignal.UNPAUSE_GAME

        return next_state

    def draw(self, screen: pygame.Surface) -> None:
        """
        Renders the pause menu composition.

        Frozen game state first, followed by the pause UI elements,
        creating a visual overlay effect.

        Args:
            screen (pygame.Surface): The target rendering surface.
        """
        # Render the frozen game state as the background layer
        self._paused_state.draw(screen)

        # Render the pause menu UI on top
        self._draw_objects(screen)
