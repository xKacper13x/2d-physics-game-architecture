import pygame
import helpers


class Button:
    def __init__(self, left, top, width, height):
        self._button_rect = pygame.Rect(left, top, width, height)

    def rect(self):
        return self._button_rect

    def load_image(self, img_path, img_size=None):
        return helpers.load_image(img_path, img_size)

    def draw(self, screen, pos):
        screen.blit(self.image, pos)

    def is_clicked():
        pass
