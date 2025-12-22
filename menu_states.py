from game_states import State, GameState
import buttons
import pygame


class TitleScreenState(State):
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.pressed_keys = []
        self._background_image = self.load_image(
            'assets/images/Title_Screen.png')
        self.create_buttons(screen_size)

    def create_buttons(self, screen_size):
        y_pos = 470
        center_x = screen_size[0] * 0.5
        spacing = 300
        size = pygame.Vector2(175, 175)
        path = 'assets/images/Title_Screen_button.png'
        font_path = 'assets/fonts/Dalek.ttf'
        font_size = 35

        pos = pygame.Vector2(center_x - spacing, y_pos)
        self._play_button = buttons.Button(pos, size, path)
        self._play_button.add_text('PLAY', font_path, font_size)

        pos = pygame.Vector2(center_x, y_pos)
        self._settings_button = buttons.Button(pos, size, path)
        self._settings_button.add_text('OPTIONS', font_path, font_size)

        pos = pygame.Vector2(center_x + spacing, y_pos)
        self._quit_button = buttons.Button(pos, size, path)
        self._quit_button.add_text('QUIT', font_path, font_size)

    def update(self, events):
        result = self
        if self._play_button.is_clicked(events):
            result = GameState(self._screen_size, 1)
        elif self._settings_button.is_clicked(events):
            pass
            # return SettingsState(self._screen_size)
        elif self._quit_button.is_clicked(events):
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
        return result

    def draw(self, screen):
        screen.blit(self._background_image, (0, 0))
        self._play_button.draw(screen)
        self._settings_button.draw(screen)
        self._quit_button.draw(screen)


class MainMenuState(State):
    def __init__(self, screen_size):
        super().__init__(screen_size)

    def update(self, events):
        return super().update(events)

    def draw(self, screen):
        super().draw(screen)
