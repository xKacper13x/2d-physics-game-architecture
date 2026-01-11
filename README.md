# My angry birds
# Author
Kacper Krzyżewski
Numer indeksu: 343027

## Description
Projekt zaliczeniowy jest grą wzorowaną na jednej z najpopularniejszych gier - Angry Birds. Oparty jest na symulacji fizycznej 2D, odwzorowującej mechanikę znanej gry zręcznościowej. Celem projektu jest demonstracja wykorzystania języka Python w połączeniu z silnikiem fizycznym Pymunk oraz biblioteką graficzną Pygame. W przeciwieństwie do prostych gier typu "arcade", ten projekt stawia na realistyczną fizykę. Każdy obiekt w grze – od drewnianej belki po przeciwnika – posiada masę, tarcie, sprężystość i moment bezwładności. Dzięki temu konstrukcje walą się w sposób naturalny, a trajektoria lotu pocisków zależy od siły naciągu i grawitacji. Zaimplementowany został system celowania poprzez rysowanie przewidywanie trajektorii lotu pocisku znany z oryginalnej gry. Gra składa się z czterech poziomów, o narastającym poziomie trudności. Każdy z poziomów został opisany w swoim pliku konfiguracyjnym json, co oznacza, że aby gra miała więcej poziomów, wystarczy dodać kolejne pliki json w poprawnym formacie.

## Visuals
![Rozgrywka](./assets/gameplay.gif)

## User Manual
Aby uruchomić program należy zainstalować wszystkie potrzebne pakiety zdefiniowane w pliku requirements.txt(np. poleceniem w terminalu pip install -r requirements.txt). Po zainstalowaniu pakietów pozostaje uruchomić plik main.py. Po uruchomieniu wyświetli się menu główne gry, zawierające trzy przycisku:
PLAY - uruchamia grę od pierwszego poziomu.
OPTIONS - Przełącza tryb wyświetlania między oknem, a pełnym ekranem. (Ze względu na niską jakość grafik wygenerowanych przez Gemini zalecane jest granie w trybie okna, w celu maksymalizacji wrażeń wizualnych.).
QUIT - Zamyka aplikację.
Po wciśnięciu przycisku PLAY, rozpocznie się właściwa gra, składająca się z czterech poziomów, polegających na naciągnięciu procy w sposób pozwalający wystrzelonemu pociskowi trafić wszystkich przeciwników. Poziomy gry obsługują również dwa klawisze:
- ESC - wstrzymuje grę i wyświetla menu pauzy, składające się z przycisków play, retry, settings(w aktualnej wersji gry nic nie robi) oraz quit level.
- F11 - Przełącza tryb wyświetlania między oknem, a pełnym ekranem.

Poziom gry kończy się, gdy zostanie spełniony jeden z następujących warunków:
- Wystrzelone zostaną wszystkie pociski - porażka, jeśli co najmniej jeden z przeciwników przetrwał, wtedy zerowane zostają punkty uzyskane w danej próbie.
- Pokonani zostaną wszyscy przeciwnicy - zwycięstwo, sprawdzenie i zapis rekordu punktowego.

Po zakończeniu poziomu wyświetlony zostaje ekran podsumowania zawierający informacje o punktach uzyskanych w danej próbie, rekordzie punktowym w danym poziomie. Stan ten daje możliwość przejście do kolejnego poziomu, w przypadku zwycięstwa. Można również restartować poziom lub wyjść do głównego menu.

Po ukończeniu wszystkich poziomów, gracz zostaje przeniesiony do menu głównego, mając opcję rozpoczęcia gry na nowo.
## Used Solutions
Gra wykorzystuje system maszyny stanów, każdy ekran jest osobnym stanem, wykonującym swoją logikę oraz przekazującym informacje o kolejnym stanie do menedżera gry.
Klasy:

AngryKnightsApp (main.py):
    Główna klasa aplikacji zarządzająca cyklem życia gry 'Angry Knights'.

    Klasa ta odpowiada za:
    - Inicjalizację biblioteki Pygame i okna gry.
    - Obsługę głównej pętli (game loop).
    - Przechwytywanie globalnych zdarzeń (np. zamknięcie okna,
                                        przełączenie pełnego ekranu).
    - Zarządzanie maszyną stanów (przełączanie między Menu, Grą, Pauzą itp)

Folder states:
    State(base_state.py):
        Bazowa klasa Stanu gry.

        Klasa ta zarządza wspólnymi elementami dla wszystkich stanów:
        - pobiera dane z pliku konfiguracyjnego json
        - ustawia tło stanu
        - tworzy podstawowe obiekty gry i rysuje je
        - aktualizuje wyniki

    Klasy dziedziczące ze State:
        MainMenuState(main_menu_state.py):
            Stan gry reprezentujący menu główne.
            Zarządza interakcją z użytkownikiem przed rozpoczęciem rozgrywki.

            Posiada trzy przyciski, które obsługuje:
            - wciśnięcie przycisku 'play' uruchamia pierwszy poziom gry
            - wciśnięcie przycisku 'options' przełącza tryb wyświetlania
                między oknem a pełnym ekranem (Fullscreen).
            - wciśnięcie przycisku 'quit' zamyka program

        GameState(game_state.py):
            Stan gry reprezentujący poziomy gry.

            Klasa ta odpowiada za:
            - Zarządzanie obiektami fizycznymi, tworzenie, aktualizowanie,
            rysowanie i niszczenie ich.
            - Inicjalizowanie przestrzeni do obliczeń fizycznych.
            - Określenie działania i zasad gry.
            - Zarządzanie wejściem pobranym od użytkownika.

        LevelCompleteState(level_complete_state.py):
            Stan podsumowania poziomu.

            Wyświetlany po zakończeniu poziomu rozgrywki.
            Prezentuje wynik punktowy, high score oraz umożliwia przejście dalej,
            restart lub wyjście.

        PauseState(pause_state.py):
            Stan gry reprezentujący menu pauzy.

            Jest to stan nakładkowy (Overlay), co oznacza, że jest wyświetlany
            "na wierzchu" zatrzymanej rozgrywki, nie usuwając jej z pamięci.

Folder entities:
    GameObject(object_base.py):
        Podstawowa klasa dla wszystkich obiektów wizualnych w grze.

        Odpowiada za wczytanie grafiki, skalowanie oraz rysowanie obiektu
        na ekranie.

    Klasy dziedziczące z GameObject:
        Slingshot(static_objects.py)
            Klasa reprezentująca procę (wyrzutnię).

            Odpowiada za:
            - Wyświetlanie grafiki procy.
            - Rysowanie gumy (cięciwy).
            - Przechowywanie informacji o sile naciągu.

        Button(ui_elements.py)
            Klasa reprezentująca interaktywny przycisk.
            Poza elementami Gameobject, dodaje obsługę kliknięć myszą.

            Klasy dziedziczące z Button:
                TextButton(ui_elements.py):
                    Przycisk z napisem w środku.
                    Rozszerza klasę Button o obiekt Text wyśrodkowany względem przycisku.

        PhysicalObject(object_base.py):
            Klasa rozszerzająca GameObject o właściwości fizyczne (Pymunk).

            Obsługuje:
            - Masę, zdrowie i zadawanie obrażeń przy zderzeniach.
            - Synchronizację pozycji graficznej z ciałem fizycznym (Pymunk Body).
            - Rotację grafiki zgodnie z fizyką.
            - Zliczanie punktów za uszkodzenia.

            Klasy dziedziczące z PhysicalObject:
                Enemy(enemy.py):
                    Klasa reprezentująca przeciwnika w grze.

                    Dziedziczy po PhysicalObject, więc posiada fizykę, zdrowie i grafikę.
                    Dodatkowo implementuje logikę natychmiastowej śmierci przy kontakcie
                    z pociskiem gracza.

                Projectile(projectile.py):
                    Klasa reprezentująca pocisk (kamień) wystrzeliwanego z procy.

                    Obsługuje:
                    - Przeciąganie myszką (naciąganie procy).
                    - Fizykę lotu (po wystrzeleniu).
                    - Wykrywanie momentu opuszczenia procy (dla animacji gumy).
                    - Obliczanie punktu zaczepienia gumy.

                Structure(structure.py):
                    Klasa reprezentująca element konstrukcyjny (blok, skrzynka, belka).

                    Są to obiekty fizyczne, które tworzą budowle chroniące przeciwników.
                    Mogą zostać zniszczone przez uderzenie, posiadają masę i tarcie.

    Text:
        Klasa reprezentująca element tekstowy w grze.

        Odpowiada za renderowanie tekstu, obsługę czcionek, kolorów
        oraz pozycjonowanie względem ekranu lub innego obiektu (np. przycisku).

    Ground:
    Klasa reprezentująca fizyczne podłoże (ziemię).
    Jest to obiekt niewidoczny, ale posiadający
    fizyczne właściwości (kolizje), które zapobiegają spadaniu obiektów
    w nieskończoność.

## Project Evaluation & Reflection
1. Podsumowanie zrealizowanych prac
Projekt udało się doprowadzić do etapu w pełni grywalnego prototypu. Zrealizowano kluczowe mechaniki:

Silnik fizyczny: Pomyślna integracja biblioteki Pymunk z warstwą wizualną Pygame. Obiekty posiadają masę, tarcie i reagują na grawitację w sposób realistyczny.

System UI: Zamiast gotowych bibliotek, zaimplementowano własny, lekki system interfejsu (klasy Button, TextButton, Text), co pozwoliło na pełną kontrolę nad wyglądem menu.

Architektura kodu: Zastosowano podejście obiektowe z podziałem na klasy bazowe (GameObject, PhysicalObject) i dziedziczące (Enemy, Structure), co ułatwia dodawanie nowych elementów.

Odporność: System ładowania zasobów (helpers.py) został zabezpieczony przed awarią – gra nie wyłącza się przy braku plików graficznych, lecz stosuje "placeholdery", co znacznie ułatwia debugowanie.

Testy jednostkowe: Kluczowe moduły pomocnicze oraz elementy UI zostały pokryte testami z wykorzystaniem frameworka pytest, co pozwoliło wyeliminować błędy.

2. Czego nie udało się osiągnąć i dlaczego
Mimo realizacji głównego celu, pewne elementy zostały pominięte ze względu na ograniczenia czasowe lub priorytetyzację kluczowych funkcjonalności:

System zapisu i wielu poziomów: Pierwotnie planowano edytor poziomów lub menu wyboru poziomu. Niestety ze względu na ograniczenia czasowe, gra wymusza liniowe przejście od pierwszego poziomu do ostatniego i nie umożliwia zapisania postępu(poza rekordem punktowym zapisywanym w pliku json).

Udźwiękowienie: Gra nie posiada efektów dźwiękowych ani muzyki. Skupiono się na warstwie wizualnej i logicznej, traktując audio jako element drugoplanowy.

3. Napotkane przeszkody i rozwiązania
Podczas prac natrafiono na kilka istotnych problemów technicznych:

Kąty Pymunk vs Pygame: Biblioteka fizyczna (Pymunk) liczy kąt obrotu w przeciwną stronę do biblioteki wizualnej (Pygame), oraz w innej jednostce(pymunk - radiany, pygame - stopnie). Problem został rozwiązany poprzez mnożenie przez -1 i zmiane jednostek przed przekazaniem obrazu do obrotu.

4. Zmiany w stosunku do planowanego rozwiązania
Projekt ewoluował w trakcie implementacji:

Odejście od róznorodności pocisków: W oryginalnej grze Angry birds użytkownik ma do wyboru wiele rodzajów ptaków o różnych zdolnościach specjalnych. Niestety ze względu na ograniczenia czasowe nie udało się zaimplementować analogicznego systemu pocisków specjalnych.

Nie udało się zrobić opisanego wcześniej menu wyboru poziomu gry.

Odejście od gotowych bibliotek UI: Zrezygnowano z użycia pygame_gui na rzecz własnej implementacji. Choć zajęło to więcej czasu, pozwoliło na lepsze zrozumienie obsługi zdarzeń myszy i kolizji w pętli gry.

Zarządzanie błędami: Początkowo gra miała zgłaszać wyjątek przy braku pliku. Zmieniono to na system "Silent Fail" z placeholderami (różowe kwadraty), co pozwala na pracę nad kodem nawet bez dostępu do finalnych grafik.
