import helpers
import entities.ui_elements as ui_elements
import exceptions
import pygame


class State:
    def __init__(self, screen_size, data):
        self._screen_size = screen_size

        self._buttons_dict = {}
        self._texts_dict = {}
        self._objects = self._initialize_objects(data)
        self._create_texts(data)

    def _initialize_objects(self, data):
        result = []

        objects_data = data['objects']
        if 'buttons' in objects_data:
            self._buttons = self._initialize_buttons(objects_data)
            result += self._buttons

        return result

    def _create_texts(self, data):
        if 'texts' in data:
            object_data = data['texts']
            for obj in object_data:
                text = ui_elements.Text(obj, self._screen_size)
                self._texts_dict[text.name()] = text

    def _update_score_labels(self):
        """
        Aktualizuje teksty wyników(bieżący i high score),
        szukając ich w słowniku po nazwie z JSONa.
        """
        score_obj = self._texts_dict.get('score_text')
        if score_obj:
            base_txt = score_obj.get_initial_text()
            new_text = base_txt + f' {self._current_score:^5}'
            score_obj.set_text(new_text)

        high_score_obj = self._texts_dict.get('high_score_text')
        if high_score_obj:
            base_txt = high_score_obj.get_initial_text()
            new_text = base_txt + f' {self._high_score:^5}'
            high_score_obj.set_text(new_text)

    def _initialize_buttons(self, data):
        object_data = data['buttons']

        created_buttons = []
        for obj in object_data:
            if 'texts' in obj.keys():
                button = ui_elements.TextButton(obj, self._screen_size)
            else:
                button = ui_elements.Button(obj, self._screen_size)

            created_buttons.append(button)
            self._buttons_dict[button.name()] = button
        return created_buttons

    def _set_background(self, img_path):
        try:
            self._background_image = self.load_image(img_path)
        except (exceptions.MissingResourceError, pygame.error):
            self._background_image = pygame.Surface(self._screen_size)
            self._background_image.fill((135, 206, 235))

    def load_image(self, img_path, img_size=None):
        if img_size is None:
            img_size = self._screen_size
        return helpers.load_image(img_path, img_size)

    def _draw_objects(self, screen):
        for obj in self._objects:
            obj.draw(screen)

    def _draw_texts(self, screen):
        for text in self._texts_dict.values():
            text.draw(screen)

    def update(self, events):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))
        screen.blit(self._background_image, (0, 0))
        self._draw_objects(screen)
        self._draw_texts(screen)
