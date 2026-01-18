from .base_service import BaseService
import json


class LevelService(BaseService):
    """
    Service responsible for level loading logic and data management.

    It decouples JSON file access from the core game logic, following the
    Separation of Concerns (SoC) principle.

    Attributes:
        config_dir (Path): Path to the directory containing level
                           configuration files.
        _current_data (dict): Dictionary storing the data
                              of the currently loaded level.
    """

    @property
    def physics_config(self) -> tuple:
        """
        Retrieves physics parameters for the current level.

        Returns:
            tuple: A tuple containing (gravity_x, gravity_y).
        """
        return (self._current_data.get('gravity_x', 0),
                self._current_data.get('gravity_y', -900))

    @property
    def high_score(self) -> int:
        """
        Retrieves the high score for the currently loaded level.

        Returns:
            int: The recorded high score. Returns 0 if not found.
        """
        return self._current_data.get('high_score', 0)

    def save_new_high_score(self, level_id: int, new_score: int) -> bool:
        """
        Saves a new high score to the JSON file
        if it exceeds the current record.

        Args:
            level_id (int): Numerical ID of the level.
            new_score (int): The score to be potentially saved.

        Returns:
            bool: True if a new high score was saved, False otherwise.
        """
        if new_score <= self.high_score:
            return False

        file_path = self._config_dir / f"level{level_id}.json"
        self._current_data['high_score'] = new_score

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._current_data, f, indent=4)
            return True
        except Exception:
            # dodać logging
            return False
