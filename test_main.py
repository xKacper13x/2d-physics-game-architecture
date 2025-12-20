from main import AngryBirdsApp


def test_screen_size():
    app = AngryBirdsApp()
    assert app.screen_size()[0] == 1920
    assert app.screen_size()[1] == 1080
