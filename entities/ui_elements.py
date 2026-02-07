from .static_objects import GameObject
import pygame
import core.helpers as helpers


class Text:
    """
    A standalone UI component for text rendering and management.

    Responsible for managing font lifecycles, color validation, and
    dynamic positioning relative to a parent surface or coordinate system.

    Attributes:
        _surface (pygame.Vector2 | pygame.Rect): The reference container
                                                 for positioning.
        _name (str): Unique identifier for the text element.
        _text (str): The currently displayed string.
        _text_color (tuple): Validated RGB color tuple.
        _font (pygame.font.Font): The Pygame font object used for rendering.
        _text_surface (pygame.Surface): The rendered text image.
        _text_rect (pygame.Rect): The bounding box for the rendered text.
    """
    def __init__(self, data: dict,
                 surface: pygame.Vector2 | pygame.Rect):
        """
        Initializes the text component with configuration data.

        Args:
            data (dict): Configuration dictionary (text, font_size, etc.).
            surface (pygame.Vector2 | pygame.Rect): The parent bounds used
                                                    for anchor calculations.
        """
        self._surface = surface
        self._name = data.get('name', '')

        text = str(data.get('text', ''))
        self._initial_text = text
        self._text = text

        self._font_path = data.get('font_path', '')
        self._font_size = data.get('font_size', 10)

        self._font_size = int(max(self._font_size, 1))

        self._font = helpers.initialize_font(self._font_path,
                                             self._font_size)

        self._anchor = data.get('anchor', 'center')

        self._x_offset = data.get('x_offset', 0)
        self._y_offset = data.get('y_offset', 0)

        text_color_R = data.get('text_color_R', 0)
        text_color_G = data.get('text_color_G', 0)
        text_color_B = data.get('text_color_B', 0)

        self.set_text_color((text_color_R, text_color_G, text_color_B))

    @property
    def name(self) -> str:
        """Returns the unique identifier of the text element."""
        return self._name

    @property
    def text(self) -> str:
        """Returns the current text content."""
        return self._text

    @property
    def text_color(self) -> tuple:
        """Returns the current RGB color tuple of the text."""
        return tuple(self._text_color)

    @property
    def initial_text(self) -> str:
        """Returns the initial template/starting text."""
        return self._initial_text

    @property
    def font_size(self) -> int:
        """Returns the current font size (integer)."""
        return self._font_size

    def _update_render(self) -> None:
        """
        Regenerates the text surface and recalculates its spatial bounds.

        Triggered automatically upon state changes (text, color, or font).
        """
        try:
            self._text_surface = self._font.render(self._text, True,
                                                   self._text_color)
        except ValueError:
            self._text_color = (0, 0, 0)
            self._text_surface = self._font.render(self._text, True,
                                                   self._text_color)

        self._text_rect = self._text_surface.get_rect()
        self._update_position()

    def _update_position(self) -> None:
        """
        Dynamically calculates the text position using anchor resolution.

        Uses reflection (setattr) to map anchor strings to Rect attributes,
        ensuring flexible UI layouts.
        """
        if isinstance(self._surface, pygame.Rect):
            self._pos = pygame.Vector2(self._surface.center)
        else:
            position = helpers.base_pos_on_anchor(self._anchor, self._surface)
            self._pos = pygame.Vector2(position)
        self._pos += pygame.Vector2(self._x_offset, self._y_offset)

        try:
            setattr(self._text_rect, self._anchor, self._pos)
        except AttributeError:
            setattr(self._text_rect, 'center', self._pos)

    def set_text(self, new_text: str = '') -> None:
        """
        Updates the text content and triggers a re-render.

        Args:
            new_text (str): The new string to be displayed.
        """
        if new_text == '':
            return

        self._text = str(new_text)
        self._update_render()

    def set_text_color(self, new_color: tuple) -> None:
        """
        Updates the text color with built-in component validation.

        Args:
            new_color (tuple): RGB tuple (R, G, B).
        """
        r, g, b = new_color

        r = helpers.validate_color(r)
        g = helpers.validate_color(g)
        b = helpers.validate_color(b)
        self._text_color = (r, g, b)

        self._update_render()

    def set_font_size(self, new_size: int | float) -> None:
        """
        Changes font size.

        Args:
            new_size (int | float): New value for size.
        """
        if isinstance(new_size, (int, float)):
            self._font_size = max(1, new_size)

            self._font = helpers.initialize_font(self._font_path,
                                                 self._font_size)
            self._update_render()

    def draw(self, screen: pygame.Surface) -> None:
        """Renders the text surface to the target screen."""
        if self._text_surface is not None:
            screen.blit(self._text_surface, self._text_rect)


class Button(GameObject):
    """
    An interactive UI element that inherits spatial properties from GameObject.

    Adds event handling for mouse interactions (hitbox collision detection).

    Attributes:
        _pos (pygame.Vector2): Center position of the button.
    """

    def __init__(self, object_data: dict, screen_size: pygame.Vector2):
        """
        Initializes the button and calculates its anchor-based position.

        Args:
            object_data (dict): Button configuration (anchor, offsets, etc.).
            screen_size (pygame.Vector2): The parent screen dimensions.
        """
        anchor = object_data.get('anchor', 'center')
        off_x = object_data.get('x_offset', 0)
        off_y = object_data.get('y_offset', 0)

        self._pos = pygame.Vector2(helpers.base_pos_on_anchor(anchor,
                                                              screen_size))
        self._pos += pygame.Vector2(off_x, off_y)
        super().__init__(object_data, self._pos)

    @property
    def size(self) -> tuple:
        """Returns the geometric extents (width, height) of the button."""
        return self._object_rect.size

    @property
    def rect(self) -> pygame.Rect:
        """Returns the interaction hitbox (Rect) of the button."""
        return self._object_rect

    def is_clicked(self, lmb_clicked: bool,
                   mouse_pos: tuple) -> bool:
        """
        Performs O(1) collision detection for mouse click events.

        Args:
            lmb_clicked (bool): Whether the Left Mouse Button was clicked.
            mouse_pos (tuple): Current (x, y) coordinates of the cursor.

        Returns:
            bool: True if the click event occurred within the button's bounds.
        """
        if lmb_clicked:
            m_collision = self._object_rect.collidepoint(mouse_pos)
            if m_collision:
                return True
        return False


class TextButton(Button):
    """
    A composite UI component consisting of an interactive Button
    and a Text label.

    Implements a fallback mechanism to ensure UI integrity
    even with missing data.
    """
    def __init__(self, object_data: dict, screen_size: pygame.Vector2):
        """
        Initializes the button and its centered text label.

        Args:
            object_data (dict): Config dictionary containing both button
                                and text data.
            screen_size (pygame.Vector2): Parent screen dimensions.
        """
        super().__init__(object_data, screen_size)
        # Handle missing or malformed text data lists
        texts_list = object_data.get('texts', [])
        if texts_list and len(texts_list) > 0:
            text_data = texts_list[0]
        else:
            text_data = {'text': 'Error', 'font_size': 35}

        self._text = Text(text_data, self._object_rect)

    def draw(self, screen):
        """Renders both the button background and its text label."""
        super().draw(screen)
        self._text.draw(screen)
