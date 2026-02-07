import json
from pathlib import Path


class BaseService:
    """
    Base service responsible for data persistence and JSON file management.

    This class serves as a foundation for specialized services, providing:
    - Centralized management of JSON file access.
    - Error handling for data loading and parsing.
    - Decoupling of file I/O operations from the core game state logic.
    - A base structure for data-driven entity initialization.

    Attributes:
        _config_dir (Path): Path to the directory containing
                           configuration files.
        _current_data (dict): Dictionary storing the data of the
                              currently loaded file.
    """
    def __init__(self, config_dir: str = "objects_config_files"):
        """
        Initializes the base service with a specific configuration directory.

        Args:
            config_dir (str): The directory path where JSON files are located.
        """
        self._config_dir = Path(config_dir)
        self._current_data = {}

    def load_data(self, config_file: str) -> dict:
        """
        Loads data from a JSON file into the internal state.

        Args:
            config_file (str): Name of the file to be loaded
                               (including extension).

        Returns:
            dict: The dictionary containing the loaded configuration data.

        Raises:
            FileNotFoundError: If the specified configuration
                               file does not exist.
            ValueError: If the specified configuration file is not JSON.
            json.JSONDecodeError: If the file content is not a valid JSON.
        """
        file_path = self._config_dir
        if file_path.is_dir():
            file_path = file_path / config_file
        try:
            if file_path.suffix != '.json':
                raise ValueError(f"Expected json file, got {file_path.suffix}")

            with open(file_path, 'r', encoding='utf-8') as file_handle:
                self._current_data = json.load(file_handle)
            return self._current_data
        except FileNotFoundError:
            # Placeholder for future logging implementation
            raise
        except ValueError:
            # Placeholder for future logging implementation
            raise
        except json.JSONDecodeError:
            # Placeholder for future logging implementation
            raise
