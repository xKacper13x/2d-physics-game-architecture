from .base_state import State
import pygame
import json


class LevelCompleteState(State):
    def __init__(self, screen_size: pygame.Vector2, completed_level: State):

        scores = completed_level.get_scores()
        self._current_score, self._high_score = scores
        self._completed_level = completed_level
        self._level = self._completed_level.get_level()

        path = 'objects_config_files/level_summary.json'
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()

        self._update_score_labels(self._current_score,
                                  self._high_score)

    def get_completed_level_state(self) -> State:
        return self._completed_level

    def get_level(self) -> State:
        return self._level

    def _create_buttons(self):
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._quit_button = self._buttons_dict['quit_button']

    def _handle_input(self, events: list) -> str:
        next_state = self
        if self._play_button.is_clicked(events):
            if self._current_score > 0:
                next_state = 'NEXT_LEVEL'
            else:
                next_state = 'RESTART_LEVEL'
        elif self._retry_button.is_clicked(events):
            next_state = 'RESTART_LEVEL'
        elif self._quit_button.is_clicked(events):
            next_state = "GO_TO_MENU"
        return next_state

    def update(self, events):
        next_state = self._handle_input(events)
        return next_state

    def draw(self, screen):
        self._completed_level.draw(screen)

        overlay = pygame.Surface((self._screen_size.x / 2,
                                  self._screen_size.y),
                                 pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        overlay_rect = overlay.get_rect()
        overlay_rect.center = (self._screen_size / 2)
        screen.blit(overlay, overlay_rect)

        self._draw_objects(screen)
        self._draw_texts(screen)
