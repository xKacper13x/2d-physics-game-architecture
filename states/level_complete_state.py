from .base_state import State
from core.signals import GameSignal
from core.input_handler import InputData
from services.base_service import BaseService
import pygame


class LevelCompleteState(State):
    """
    Manages the 'Level Summary' interface displayed upon level completion.

    This state acts as an overlay, rendering on top of the frozen game world.
    It presents performance metrics (score, high score) and offers navigation
    options (Next Level, Retry, Quit) based on player success.

    Attributes:
        _current_score (int): Points achieved in the just-concluded session.
        _high_score (int): Historical record for the level.
        _level (int): Numeric identifier of the completed level.
        _completed_level (State): Reference to the previous GameState instance,
                                  used for background rendering (Snapshot).
        _overlay (pygame.Surface): Semi-transparent surface for visual dimming.
    """
    def __init__(self, screen_size: pygame.Vector2, completed_level: State):
        """
        Initializes the summary state using data from the finished session.

        Args:
            screen_size (pygame.Vector2): Dimensions of the application window.
            completed_level (State): The game state instance that just ended.
                                     Used to extract scoring data and render
                                     the background context.
        """
        scores = completed_level.scores
        self._current_score, self._high_score = scores
        self._completed_level = completed_level
        self._level = self._completed_level.level

        path = 'level_summary.json'
        service = BaseService()
        data = service.load_data(path)
        super().__init__(screen_size, data)
        self._create_buttons()

        self._update_score_labels(self._current_score,
                                  self._high_score)

        self._overlay = pygame.Surface((self._screen_size.x / 2,
                                        self._screen_size.y),
                                       pygame.SRCALPHA)

    @property
    def completed_level_state(self) -> State:
        """Returns the reference to the frozen game state."""
        return self._completed_level

    @property
    def level(self) -> int:
        """Returns the ID of the level being summarized."""
        return self._level

    def _create_buttons(self) -> None:
        """
        Maps generic button references to
        attributes for logic handling.
        """
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._quit_button = self._buttons_dict['quit_button']

    def _handle_input(self, input_data: InputData) -> GameSignal:
        """
        Processes user interaction with the summary UI.

        Determines the next state transition based on button clicks:
        - Play: Advances to the next level if score > 0, else restarts.
        - Retry: Reloads the current level immediately.
        - Quit: Returns to the main menu.

        Args:
            input_data (InputData): Snapshot of current frame inputs
                                    (mouse state, position).

        Returns:
            GameSignal: Command indicating the desired state transition.
        """
        next_state = GameSignal.STAY
        if self._play_button.is_clicked(input_data.lmb_clicked,
                                        input_data.mouse_pos):
            # Conditional logic: Can only proceed
            # if the level was actually passed
            if self._current_score > 0:
                next_state = GameSignal.NEXT_LEVEL
            else:
                next_state = GameSignal.RESTART_LEVEL
        elif self._retry_button.is_clicked(input_data.lmb_clicked,
                                           input_data.mouse_pos):
            next_state = GameSignal.RESTART_LEVEL
        elif self._quit_button.is_clicked(input_data.lmb_clicked,
                                          input_data.mouse_pos):
            next_state = GameSignal.GO_TO_MENU
        return next_state

    def draw(self, screen: pygame.Surface) -> None:
        """
        Main logic step for the summary screen.

        Args:
            input_data (InputData): Snapshot of current frame inputs.

        Returns:
            GameSignal: Signal for the main application loop.
        """
        # 1. Background Layer (The frozen game world)
        self._completed_level.draw(screen)

        # 2. Overlay Layer (Dimming effect)
        self._overlay.fill((0, 0, 0, 215))
        overlay_rect = self._overlay.get_rect()
        overlay_rect.center = (self._screen_size / 2)
        screen.blit(self._overlay, overlay_rect)

        # 3. UI Layer
        self._draw_objects(screen)
        self._draw_texts(screen)
