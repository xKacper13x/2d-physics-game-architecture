import core.helpers as helpers
import entities.ui_elements as ui_elements
from core.input_handler import InputData
from core.signals import GameSignal
import exceptions
import pygame


class State:
    """
    Abstract base class for all game states (e.g., Menu, Gameplay, Pause).

    The State class serves as an orchestration layer responsible for:
    - Managing state-specific lifecycles (Update/Draw).
    - Data-driven initialization of UI components and game objects
      from configuration data.
    - Handling background resource loading and fallback mechanisms.
    - Providing centralized label management for real-time score updates.

    Attributes:
        _screen_size (pygame.Vector2): The logical resolution
                                        of the game window.
        _buttons_dict (dict): A registry of active buttons
                                mapping names to objects.
        _texts_dict (dict): A registry of active text labels
                                mapping names to objects.
        _objects (list): A collection of renderable entities
                            currently in the state.
        _background_image (pygame.Surface): The processed background surface.
    """
    def __init__(self, screen_size: pygame.Vector2, data: dict):
        """
        Initializes the state context and bootstraps UI/game components.

        Args:
            screen_size (pygame.Vector2): Desired screen dimensions.
            data (dict): State configuration data extracted from JSON/Dict
                            source.
        """
        if screen_size.x > 0 and screen_size.y > 0:
            self._screen_size = screen_size
        else:
            self._screen_size = pygame.Vector2(1920, 1080)

        self._buttons_dict = {}
        self._texts_dict = {}
        self._objects = self._initialize_objects(data)
        self._create_texts(data)

    def _initialize_objects(self, data: dict) -> list:
        """
        Parses configuration data to instantiate game objects.

        Args:
            data (dict): The configuration source.

        Returns:
            list: A collection of instantiated game objects.
        """
        result = []

        objects_data = data.get('objects', {})
        if 'buttons' in objects_data:
            buttons = self._initialize_buttons(objects_data)
            result += buttons

        return result

    def _initialize_buttons(self, data: dict) -> list:
        """
        Factory method to create buttons and register them
        in the state registry.

        Distinguishes between standard Buttons and TextButtons based on
        the presence of text metadata.

        Args:
            data (dict): Button configuration dictionary.

        Returns:
            list: A list of instantiated button objects.
        """
        object_data = data['buttons']

        created_buttons = []
        for obj in object_data:
            if 'texts' in obj.keys():
                button = ui_elements.TextButton(obj, self._screen_size)
            else:
                button = ui_elements.Button(obj, self._screen_size)

            created_buttons.append(button)
            self._buttons_dict[button.name] = button
        return created_buttons

    def _create_texts(self, data: dict) -> None:
        """
        Instantiates text components and registers them in the state registry.

        Args:
            data (dict): Text configuration source.
        """
        if 'texts' in data:
            object_data = data['texts']
            for obj in object_data:
                text = ui_elements.Text(obj, self._screen_size)
                self._texts_dict[text.name] = text

    def _update_score_labels(self, curr_score: int, high_score: int) -> None:
        """
        Synchronizes score-related UI labels with current game values.

        Utilizes string formatting and label registry lookup for
        efficient UI updates.

        Args:
            curr_score (int): The current player score.
            high_score (int): The historical maximum score.
        """
        score_obj = self._texts_dict.get('score_text')
        if score_obj:
            base_txt = score_obj.initial_text
            new_text = base_txt + f' {curr_score:^5}'
            score_obj.set_text(new_text)

        high_score_obj = self._texts_dict.get('high_score_text')
        if high_score_obj:
            base_txt = high_score_obj.initial_text
            new_text = base_txt + f' {high_score:^5}'
            high_score_obj.set_text(new_text)

    def _set_background(self, img_path: str) -> None:
        """
        Loads the background asset with a fallback
        mechanism for missing resources.

        Args:
            img_path (str): Filepath to the background image.
        """
        try:
            self._background_image = helpers.load_image(img_path,
                                                        self._screen_size)
        except (exceptions.MissingResourceError, pygame.error):
            self._background_image = pygame.Surface(self._screen_size)
            self._background_image.fill((255, 102, 255))

    def _draw_objects(self, screen: pygame.Surface) -> None:
        """
        Orchestrates the rendering of all registered game objects.

        Args:
            screen (pygame.Surface): Target rendering context.
        """
        for obj in self._objects:
            obj.draw(screen)

    def _draw_texts(self, screen: pygame.Surface) -> None:
        """
        Orchestrates the rendering of all registered text labels.

        Args:
            screen (pygame.Surface): Target rendering context.
        """
        for text in self._texts_dict.values():
            text.draw(screen)

    def _handle_input(self, input_data: InputData) -> GameSignal:
        """
        Placeholder for input handling logic.
        Intended to be overridden by subclasses (Template Method Pattern).

        Args:
            input_data (InputData): Snapshot of current frame inputs.

        Returns:
            GameSignal: Default return value is STAY.
        """
        return GameSignal.STAY

    def update(self, input_data: InputData) -> GameSignal:
        """
        The per-frame logic update hook.
        Delegates to the overridable input handler.

        Args:
            input_data (InputData): Current frame input snapshot.

        Returns:
            GameSignal: A signal to the main app indicating state transition.
        """
        return self._handle_input(input_data)

    def draw(self, screen: pygame.Surface) -> None:
        """
        The per-frame rendering hook. Manages background
        and sub-component drawing.

        Args:
            screen (pygame.Surface): Target rendering context.
        """
        screen.fill((255, 255, 255))
        screen.blit(self._background_image, (0, 0))
        self._draw_objects(screen)
        self._draw_texts(screen)
