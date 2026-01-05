from helpers import (check_path, check_size)
import exceptions
import pytest


def test_check_path_invalid():
    with pytest.raises(exceptions.MissingResourceError):
        check_path('ok')


def test_check_size_invalid_int():
    with pytest.raises(exceptions.InvalidConfigurationError):
        check_size(0)


def test_check_size_invalid_tuple_x():
    with pytest.raises(exceptions.InvalidConfigurationError):
        check_size((0, 5))


def test_check_size_invalid_tuple_y():
    with pytest.raises(exceptions.InvalidConfigurationError):
        check_size((5, 0))


def test_check_size_unsupported_type():
    with pytest.raises(exceptions.InvalidConfigurationError):
        check_size([2, 5, 4])
