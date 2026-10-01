import yaml
from pathlib import Path


class Config:
    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(config_path)
        self._data = self._load_yaml()

        # ---- Database ----
        self.DB_TYPE = self.get("database.type")
        self.HOST = self.get("database.host")
        self.USER = self.get("database.user")
        self.PASSWORD = self.get("database.password")
        self.DATABASE = self.get("database.database")

    # ---------------------
    # Internal helpers
    # ---------------------
    def _load_yaml(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with self.config_path.open("r") as f:
            return yaml.safe_load(f) or {}

    def get(self, dotted_key, default=None):
        """Read a nested value like "database.host", or return default if it is missing."""
        keys = dotted_key.split(".")
        value = self._data

        for k in keys:
            if not isinstance(value, dict) or k not in value:
                return default
            value = value[k]

        return value

    def as_dict(self):
        return self._data
