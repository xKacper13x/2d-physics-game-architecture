from main import AngryKnightsApp


def test_screen_size():
    app = AngryKnightsApp()
    assert app.screen_size()[0] == 1920
    assert app.screen_size()[1] == 1080
