import pygame
from dataclasses import dataclass


@dataclass
class InputData:
    mouse_pos: tuple
    lmb_pressed: bool
    lmb_clicked: bool
    lmb_released: bool
    key_esc_down: bool
    key_F11_down: bool


class InputHandler:
    def process_data(self, events: list) -> InputData:
        lmb_clicked = False
        lmb_released = False
        key_esc_down = False
        key_F11_down = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmb_clicked = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    lmb_released = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                key_esc_down = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                key_F11_down = True

        lmb_pressed = pygame.mouse.get_pressed()[0]
        input_data = InputData(pygame.mouse.get_pos(), lmb_pressed,
                               lmb_clicked, lmb_released, key_esc_down,
                               key_F11_down)

        return input_data
