from .base_state import State
import json
import pygame


class MainMenuState(State):
    def __init__(self, screen_size):
        with open('objects_config_files/menu.json') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()
            background_img_path = data["background_img"]
            self._set_background(background_img_path)

    def _create_buttons(self):
        self._play_button = self._buttons_dict['play_menu_button']
        self._options_button = self._buttons_dict['options_menu_button']
        self._quit_button = self._buttons_dict['quit_menu_button']

    def update(self, events):
        next_state = self
        if self._play_button.is_clicked(events):
            next_state = 'START_GAME'
        elif self._options_button.is_clicked(events):
            new_event = pygame.event.Event(pygame.KEYDOWN)
            new_event.key = pygame.K_F11
            pygame.event.post(new_event)
        elif self._quit_button.is_clicked(events):
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
        return next_state
