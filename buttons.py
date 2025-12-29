from game_objects import GameObject
import pygame
import helpers


class Button(GameObject):
    def __init__(self, pos, size, img_path):
        super().__init__(pos, size, img_path)
        self._text_surface = None
        self._text_rect = None

    def size(self):
        return self._object_rect.size

    def rect(self):
        return self._object_rect

    def draw(self, screen):
        super().draw(screen)
        if self._text_surface is not None:
            screen.blit(self._text_surface, self._text_rect)

    def is_clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    m_collision = self._object_rect.collidepoint(event.pos)
                    if m_collision:
                        return True
        return False

    def add_text(self, text, font_path, font_size):
        self._button_font = helpers.initialize_font(font_path, font_size)
        text_color = (235, 213, 174)
        self._text_surface = self._button_font.render(text, True, text_color)
        self._text_rect = self._text_surface.get_rect()
        self._text_rect.center = (self._object_rect.center)
