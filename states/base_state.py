import helpers
import entities.ui_elements as ui_elements
from core.input_handler import InputData
from core.signals import GameSignal
import exceptions
import pygame


class State:
    """
    Bazowa klasa Stanu gry.

    Klasa ta zarządza wspólnymi elementami dla wszystkich stanów:
    - pobiera dane z pliku konfiguracyjnego json
    - ustawia tło stanu
    - tworzy podstawowe obiekty gry i rysuje je
    - aktualizuje wyniki

    Attributes:
        _screen_size (pygame.Vector2): Wymiary okna gry.
        _buttons_dict (dict): Słownik utworzonych przycisków w formacie
                                {nazwa przycisku: obiekt przycisku}.
        _texts_dict (dict): Słownik utworzonych tekstów w formacie
                                {nazwa tekstu: obiekt tekstu}.
        _objects (list): Lista obiektów widocznych na ekranie.
        _background_image (pygame.Surface): Obraz tła dla danego stanu.
    """
    def __init__(self, screen_size: pygame.Vector2, data: dict):
        """
        Inicjalizuje bazowy obiekt stanu, zapisuje rozmiar okna gry,
        wywołuje metody tworzące wspólne dla wszystkich stanów obiekty
        (przyciski, teksty).

        Args:
            screen_size (pygame.Vector2): Rozmiar okna gry.
            data (dict): Słownik danych konfiguracyjnych stanu.
        """
        if screen_size.x > 0 and screen_size.y > 0:
            self._screen_size = screen_size
        else:
            self._screen_size = pygame.Vector2(1920, 1080)

        self._buttons_dict = {}
        self._texts_dict = {}
        self._objects = self._initialize_objects(data)
        self._create_texts(data)

    def _initialize_objects(self, data: dict) -> list:
        """
        Wywołuje metodę tworzącą przyciski, dodaje je do słownika
        oraz dołącza listę przycisków do listy widocznych obiektów.

        Args:
            data (dict): Słownik danych konfiguracyjnych stanu.

        Returns:
            list: Lista widocznych obiektów w stanie.
        """
        result = []

        objects_data = data.get('objects', {})
        if 'buttons' in objects_data:
            buttons = self._initialize_buttons(objects_data)
            result += buttons

        return result

    def _initialize_buttons(self, data: dict) -> list:
        """
        Tworzy obiekty przycisków dla pobranych danych i dodaje je do listy i
        słownika wszystkich przycisków w stanie
        (w formacie {nazwa przycisku: obiekt przycisku}).
        Zwraca listę przycisków.

        Args:
            data (dict): Słownik danych konfiguracyjnych stanu.
        """
        object_data = data['buttons']

        created_buttons = []
        for obj in object_data:
            if 'texts' in obj.keys():
                button = ui_elements.TextButton(obj, self._screen_size)
            else:
                button = ui_elements.Button(obj, self._screen_size)

            created_buttons.append(button)
            self._buttons_dict[button.name] = button
        return created_buttons

    def _create_texts(self, data: dict) -> None:
        """
        Tworzy obiekty tekstów dla pobranych danych i dodaje je do słownika
        wszystkich tekstów w stanie (w formacie {nazwa tekstu: obiekt tekstu}).

        Args:
            data (dict): Słownik danych konfiguracyjnych stanu.
        """
        if 'texts' in data:
            object_data = data['texts']
            for obj in object_data:
                text = ui_elements.Text(obj, self._screen_size)
                self._texts_dict[text.name] = text

    def _update_score_labels(self, curr_score: int, high_score: int) -> None:
        """
        Aktualizuje teksty wyników(bieżący i high score),
        szukając ich w słowniku po nazwie.

        Args:
            curr_score (int): Aktualny wynik.
            high_score (int): Rekord punktowy w historii gry.
        """
        score_obj = self._texts_dict.get('score_text')
        if score_obj:
            base_txt = score_obj.initial_text
            new_text = base_txt + f' {curr_score:^5}'
            score_obj.set_text(new_text)

        high_score_obj = self._texts_dict.get('high_score_text')
        if high_score_obj:
            base_txt = high_score_obj.initial_text
            new_text = base_txt + f' {high_score:^5}'
            high_score_obj.set_text(new_text)

    def _set_background(self, img_path: str) -> None:
        """
        Wczytuje obraz z podanej ścieżki i zapisuje go, jako tło stanu.
        W przypadku braku lub występowaniu błędnego pliku w podanej ścieżce,
        ustawia tło na różowy prostokąt.

        Args:
            img_path (str): Ścieżka do pliku z tłem.
        """
        try:
            self._background_image = helpers.load_image(img_path,
                                                        self._screen_size)
        except (exceptions.MissingResourceError, pygame.error):
            self._background_image = pygame.Surface(self._screen_size)
            self._background_image.fill((255, 102, 255))

    def _draw_objects(self, screen: pygame.Surface) -> None:
        """
        Wywołuje dla każdego z utworzonych w stanie obiektów metodę draw,
        wyświetlającą go na przekazanym ekranie.

        Args:
            screen (pygame.Surface): Ekran, na którym mają
                                     zostać wyświetlone obiekty.
        """
        for obj in self._objects:
            obj.draw(screen)

    def _draw_texts(self, screen: pygame.Surface) -> None:
        """
        Wywołuje dla każdego z utworzonych w stanie tekstów metodę draw,
        wyświetlającą go na przekazanym ekranie.

        Args:
            screen (pygame.Surface): Ekran, na którym mają
                                     zostać wyświetlone teksty.
        """
        for text in self._texts_dict.values():
            text.draw(screen)

    def update(self, input_data: InputData) -> GameSignal:
        return GameSignal.STAY

    def draw(self, screen: pygame.Surface) -> None:
        """
        Wyświetla tło stanu oraz wywołuje metody rysujące na podanym ekranie,
        obiekty i teksty ze stanu.

        Args:
            screen (pygame.Surface): Ekran, na którym mają
                                     zostać wyświetlone teksty.
        """
        screen.fill((255, 255, 255))
        screen.blit(self._background_image, (0, 0))
        self._draw_objects(screen)
        self._draw_texts(screen)
