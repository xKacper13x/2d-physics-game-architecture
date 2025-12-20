import pygame


class Button:
    def __init__(self, left, top, width, height):
        self._button_rect = pygame.Rect(left, top, width, height)

    def rect(self):
        return self._button_rect
