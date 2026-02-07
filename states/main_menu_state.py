from .base_state import State
from services.base_service import BaseService
from core.input_handler import InputData
from core.signals import GameSignal
import pygame


class MainMenuState(State):
    """
    Represents the main menu state, serving as the application's entry point.

    This class manages user interaction prior to gameplay initialization.
    It orchestrates:
    - Transitioning to the active game loop (Play).
    - Toggling display modes via event injection (Options/F11).
    - Graceful application termination (Quit).

    Attributes:
        _play_button (TextButton): UI component triggering
                                    the game start sequence.
        _options_button (TextButton): UI component for toggling
                                        Fullscreen/Windowed mode.
        _quit_button (TextButton): UI component for terminating
                                    the application process.
    """
    def __init__(self, screen_size: pygame.Vector2):
        """
        Bootstraps the menu state context.

        Loads UI configuration via BaseService and initializes the visual
        environment (backgrounds, buttons) using the parent State logic.

        Args:
            screen_size (pygame.Vector2): Dimensions of the application window.
        """
        service = BaseService()
        data = service.load_data('menu.json')
        super().__init__(screen_size, data)
        self._create_buttons()
        background_img_path = data["background_img"]
        self._set_background(background_img_path)

    def _create_buttons(self) -> None:
        """
        Maps generic button references from the registry to specific
        class attributes.

        This aliasing improves code readability and provides semantic access
        to specific UI controls (Play, Options, Quit).
        """
        self._play_button = self._buttons_dict['play_menu_button']
        self._options_button = self._buttons_dict['options_menu_button']
        self._quit_button = self._buttons_dict['quit_menu_button']

    def _handle_input(self, input_data: InputData) -> GameSignal:
        """
        Processes raw input data to determine the next state.

        - 'Play' triggers a direct state transition to gameplay.
        - 'Options' injects an F11 key event for display mode toggling.
        - 'Quit' injects a system QUIT event for graceful shutdown.

        Args:
            input_data (InputData): Snapshot of current frame inputs.

        Returns:
            GameSignal: The command indicating the next application state.
        """
        next_state = GameSignal.STAY
        if self._play_button.is_clicked(input_data.lmb_clicked,
                                        input_data.mouse_pos):
            next_state = GameSignal.START_GAME

        elif self._options_button.is_clicked(input_data.lmb_clicked,
                                             input_data.mouse_pos):
            new_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11)
            pygame.event.post(new_event)

        elif self._quit_button.is_clicked(input_data.lmb_clicked,
                                          input_data.mouse_pos):
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
        return next_state

    def draw(self, screen: pygame.Surface) -> None:
        """
        Delegates rendering to the base State class orchestration.

        Args:
            screen (pygame.Surface): The target rendering surface.
        """
        super().draw(screen)
