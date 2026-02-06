import pytest
from unittest.mock import patch, MagicMock
from states.main_menu_state import MainMenuState
from states.game_state import GameState
from states.pause_state import PauseState
from core.signals import GameSignal
from main import AngryKnightsApp
import pygame


# --- Side Effects (Lightweight Initializers) ---

def fast_game_init(self, screen_size, level=1):
    """
    Side effect for GameState.__init__.

    It bypasses the heavy loading logic (physics, images, JSON parsing)
    and sets only the attributes required for state transition logic.

    Args:
        screen_size (tuple): The dimensions of the screen.
        level (int): Current level number.
    """
    self._level = level
    self._screen_size = screen_size
    return None


def fast_menu_init(self, screen_size):
    """
    Side effect for MainMenuState.__init__.
    Initializes the state without loading UI assets or background music.
    """
    self.screen_size = screen_size
    return None


def fast_pause_init(self, screen_size, paused_state):
    """
    Side effect for PauseState.__init__.
    Prevents the creation of the semi-transparent overlay surface.
    """
    self._screen_size = screen_size
    self._paused_state = paused_state


# --- Fixtures ---

@pytest.fixture
def headless_app():
    """
    Creates an instance of AngryKnightsApp in a 'headless' mode.

    This fixture mocks `pygame.display` methods to prevent the application
    from opening a real window or initializing the video driver. This is
    essential for running tests in CI/CD environments.

    Returns:
        AngryKnightsApp: A safe-to-test application instance with a
                         mocked screen object (1920x1080).
    """
    with patch('pygame.display.set_mode') as mock_set_mode, \
         patch('pygame.display.set_icon'), \
         patch('pygame.display.set_caption'):

        mock_screen = MagicMock()
        mock_screen.get_width.return_value = 1920
        mock_screen.get_height.return_value = 1080
        mock_set_mode.return_value = mock_screen

        app = AngryKnightsApp()
        app._screen_size = pygame.Vector2(100, 100)
        return app


@pytest.fixture(autouse=True)
def mock_dependencies():
    """
    Automatically mocks the __init__ methods of all tested State classes.

    This fixture replaces the real constructors with lightweight 'side effects'
    (fast_game_init, etc.). This ensures that creating a State object during
    testing does not trigger asset loading, physics simulation, or file I/O.

    'autospec=True' is used to ensure the mocks adhere to the method signatures
    of the original classes (preventing missing 'self' argument errors).
    """
    with patch.object(GameState, '__init__',
                      side_effect=fast_game_init, autospec=True), \
         patch.object(MainMenuState, '__init__',
                      side_effect=fast_menu_init, autospec=True), \
         patch.object(PauseState, '__init__',
                      side_effect=fast_pause_init, autospec=True):
        yield


def test_start_game(headless_app):
    """
    Verifies that the START_GAME signal transitions the application
    from the current state to a new GameState instance.
    """
    next_state = headless_app._manage_states(GameSignal.START_GAME)
    assert isinstance(next_state, GameState)
    assert next_state.level == 1


def test_manage_states_stay(headless_app):
    """
    Verifies that the STAY signal keeps application in the current state.
    """
    initial_state = MainMenuState(headless_app.screen_size)
    headless_app._state = initial_state

    new_state = headless_app._manage_states(GameSignal.STAY)

    assert new_state == initial_state


def test_manage_states_pause_game(headless_app):
    """
    Verifies that PAUSE_GAME signal transitions the application
    from the current state to a new PauseState instance.
    """
    initial_state = GameState(headless_app.screen_size, 1)
    headless_app._state = initial_state

    new_state = headless_app._manage_states(GameSignal.PAUSE_GAME)
    assert isinstance(new_state, PauseState)


def test_manage_states_next_level(headless_app):
    """
    Verifies that NEXT_LEVEL signal transitions the application
    from the current GameState to the new GameState instance
    (with higher level index).
    """
    initial_state = GameState(headless_app.screen_size, 1)
    headless_app._state = initial_state

    new_state = headless_app._manage_states(GameSignal.NEXT_LEVEL)
    assert isinstance(new_state, GameState)
    assert new_state.level == 2


def test_quit_level(headless_app):
    """
    Verifies that GO_TO_MENU signal transitions the application from
    the current state to a new MainMenuState instance.
    """
    next_level = headless_app._manage_states(GameSignal.GO_TO_MENU)
    assert isinstance(next_level, MainMenuState)
