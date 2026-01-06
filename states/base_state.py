import helpers
import entities.ui_elements as ui_elements


class State:
    def __init__(self, screen_size, data):
        self._screen_size = screen_size

        self._buttons_dict = {}
        self._texts_dict = {}
        self._objects = self._initialize_objects(data)
        self._texts = self._initialize_texts(data)

    def _initialize_objects(self, data):
        result = []

        objects_data = data['objects']
        if 'buttons' in objects_data:
            self._buttons = self._initialize_buttons(objects_data)
            result += self._buttons

        return result

    def _initialize_texts(self, data):
        created_texts = []
        if 'texts' in data:
            object_data = data['texts']

            created_texts = []
            for obj in object_data:
                text = ui_elements.Text(obj, self._screen_size)

                created_texts.append(text)
                self._texts_dict[text.name()] = text
        return created_texts

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
        self._background_image = self.load_image(img_path)

    def load_image(self, img_path, img_size=None):
        if img_size is None:
            img_size = self._screen_size
        return helpers.load_image(img_path, img_size)

    def _draw_objects(self, screen):
        for obj in self._objects:
            obj.draw(screen)

    def _draw_texts(self, screen):
        for text in self._texts:
            text.draw(screen)

    def update(self, events):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))
        screen.blit(self._background_image, (0, 0))
        self._draw_objects(screen)
        self._draw_texts(screen)
