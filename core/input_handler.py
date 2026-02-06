import pygame
from dataclasses import dataclass


@dataclass
class InputData:
    """
    A Data Transfer Object (DTO) representing a snapshot of user input states.

    This class encapsulates mouse coordinates and the current status of
    monitored buttons and keys, providing a clean interface for game states
    to consume input data.

    Attributes:
        mouse_pos (tuple): Current (x, y) coordinates of the mouse cursor.
        lmb_pressed (bool): True if the Left Mouse Button
                            is currently held down.
        lmb_clicked (bool): True if the Left Mouse Button was pressed
                            in the current frame.
        lmb_released (bool): True if the Left Mouse Button
                             was released in the current frame.
        key_esc_down (bool): True if the Escape key
                             was pressed in the current frame.
        key_F11_down (bool): True if the F11 key was pressed
                             in the current frame.
    """
    mouse_pos: tuple
    lmb_pressed: bool
    lmb_clicked: bool
    lmb_released: bool
    key_esc_down: bool
    key_F11_down: bool


class InputHandler:
    """
    A service class responsible for translating low-level Pygame events into
    high-level InputData structures.
    """
    def process_data(self, events: list) -> InputData:
        """
        Parses a list of raw Pygame events and returns an InputData object.

        This method monitors specific mouse and keyboard events to determine
        one-time actions (clicks/releases) while polling the mouse state
        for continuous inputs.

        Args:
            events (list): A list of pygame.event.Event objects retrieved from
                           the Pygame event queue.

        Returns:
            InputData: An immutable-like snapshot containing the state of
                       monitored inputs for the current frame.
        """
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
