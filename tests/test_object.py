import pygame
import pymunk
import os
from entities.objects_base import PhysicalObject

# Nazwa tymczasowego obrazka
TEMP_IMG = "test_img_temp.png"


def create_dummy_image():
    """Pomocnicza funkcja tworząca prawdziwy plik graficzny."""
    pygame.init()
    # Tworzymy czerwoną kropkę 10x10
    surf = pygame.Surface((10, 10))
    surf.fill((255, 0, 0))
    pygame.image.save(surf, TEMP_IMG)


def delete_dummy_image():
    """Sprzątanie po testach."""
    if os.path.exists(TEMP_IMG):
        os.remove(TEMP_IMG)


def test_physical_object_logic():
    create_dummy_image()
    space = pymunk.Space()

    # Dane testowe z błędem (ujemna masa), żeby sprawdzić naprawę
    data = {
        'name': 'TestBox',
        'img_path': TEMP_IMG,
        'pos_x': 50,
        'pos_y': 50,
        'mass': -100,  # Błędna masa
        'health': 100
    }

    try:
        obj = PhysicalObject(space, data)
        obj._pos = (data['pos_x'], data['pos_y'])

        # Musimy ręcznie dodać ciało fizyczne, bo klasa bazowa tego nie robi
        # (normalnie robi to klasa dziedzicząca, np. Box)
        obj._body = pymunk.Body(1, 1)
        obj._body.position = (50, 50)

        # Sprawdzenie czy masa została naprawiona (min. 1)
        assert obj.get_mass() == 1

        # Sprawdzenie czy obiekt ma pełne życie
        assert obj._health == 100

        obj._take_damage(20)

        # Życie powinno spaść do 80
        assert obj._health == 80

        # Punkty powinny się naliczyć (20 obrażeń * 3 = 60 pkt)
        assert obj.collect_points() == 60

        # Po pobraniu punktów licznik powinien wrócić do 0
        assert obj.collect_points() == 0

        # --- Test śmierci (Update) ---
        # Ustawiamy życie na 0
        obj._take_damage(80)
        assert obj._health == 0

        # Wywołujemy update
        kill_list = []
        obj.update(kill_list)

        # Obiekt powinien dodać się do listy do usunięcia
        assert obj in kill_list

    finally:
        # CLEANUP - Sprzątanie (nawet jak test wywali błąd)
        delete_dummy_image()


def test_missing_data_error():
    """Sprawdza czy program wyrzuci błąd przy braku kluczowych danych."""
    create_dummy_image()
    space = pymunk.Space()

    bad_data = {
        'name': 'BadBox',
        # Brak img_path
    }

    try:
        # Oczekujemy, że helpers.load_image wyrzuci błąd lub pygame nie załaduje pliku
        with pytest.raises(Exception):
            PhysicalObject(space, bad_data)

    finally:
        delete_dummy_image()