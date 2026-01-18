import json
from services.level_service import LevelService
import pathlib
import pytest


def test_level_service_physics_config(tmp_path):
    """Verifies that gravity data is correctly parsed from JSON."""
    d = tmp_path / "configs"
    d.mkdir()
    config_file = d / "level1.json"
    config_file.write_text(json.dumps({
        "gravity_x": 10,
        "gravity_y": -500,
        "high_score": 1000
    }))

    service = LevelService(config_dir=str(d))
    service.load_data("level1.json")

    assert service.physics_config == (10, -500)
    assert isinstance(service.physics_config, tuple)


def test_level_service_physics_config_default(tmp_path):
    """
    Validates fallback values when gravity keys
    are missing in the configuration.
    """
    d = tmp_path / "configs"
    d.mkdir()
    config_file = d / "level1.json"
    config_file.write_text(json.dumps({
        "high_score": 1000
    }))

    service = LevelService(config_dir=str(d))
    service.load_data("level1.json")

    assert service.physics_config == (0, -900)
    assert isinstance(service.physics_config, tuple)


def test_save_new_high_score_logic(tmp_path):
    """
    Tests the logic for updating the level's record.
    """
    d = tmp_path / "configs"
    d.mkdir()
    config_file = d / "level1.json"
    config_file.write_text(json.dumps({"high_score": 500}))

    service = LevelService(config_dir=str(d))
    service.load_data("level1.json")

    assert service.save_new_high_score(1, 300) is False
    assert service.save_new_high_score(1, 700) is True


def test_double_file_name_given(tmp_path):
    """
    Checks if load_data() handles user giving file's name twice.
    Should run without exceptions.
    """
    d = tmp_path / "configs"
    d.mkdir()
    config_file = d / "level1.json"
    config_file.write_text(json.dumps({"high_score": 500}))

    path = pathlib.Path(d) / 'level1.json'
    service = LevelService(path)
    data = service.load_data(path)
    assert data['high_score'] == 500


def test_invalid_path(tmp_path):
    """
    Exercises defensive programming triggers.

    Confirms that ValueError and FileNotFoundError are raised
    for incorrect extensions or missing files.
    """
    d = tmp_path / "configs"
    d.mkdir()
    service = LevelService(config_dir=str(d))

    with pytest.raises(ValueError):
        service.load_data("level1.txt")

    with pytest.raises(FileNotFoundError):
        service.load_data("level.json")


def test_load_corrupted_json(tmp_path):
    """
    Validates the parsing layer's resilience.

    Ensures that json.JSONDecodeError is correctly surfaced
    when encountering malformed data.
    """
    d = tmp_path / "configs"
    d.mkdir()

    corrupted_file = d / 'level1.json'
    corrupted_file.write_text('kkkk')

    service = LevelService(corrupted_file)
    with pytest.raises(json.JSONDecodeError):
        service.load_data(corrupted_file)
