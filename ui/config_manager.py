import json
import os
from pathlib import Path


class ConfigManager:
        """Manages nonogram puzzle configurations. Automatically save/load configurations."""

        DEFAULT_CONFIG_FILE = "nonogram_config.json"
        DEFAULT_WIDTH = 4
        DEFAULT_HEIGHT = 4

        def __init__(self, config_file=None):
                self.config_file = config_file or self.DEFAULT_CONFIG_FILE
                self.config = {
                        "width": self.DEFAULT_WIDTH,
                        "height": self.DEFAULT_HEIGHT,
                        "rows": {},
                        "columns": {},
                }
                self.set_dimensions(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        def ensure_startup_config(self):
                """Guarantee a config file exists, or else create a blank layout."""
                config_path = Path(self.config_file)
                if config_path.exists():
                        return
                self.config = {
                        "width": self.DEFAULT_WIDTH,
                        "height": self.DEFAULT_HEIGHT,
                        "rows": {},
                        "columns": {},
                }
                self.set_dimensions(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
                self.save_config()

        def load_config(self, filepath=None):
                """Load configuration from a JSON file."""
                file_to_load = filepath or self.config_file
                if os.path.exists(file_to_load):
                        try:
                                with open(file_to_load, "r") as f:
                                        self.config = json.load(f)
                                return True
                        except Exception as e:
                                print(f"Error loading config: {e}")
                                return False
                return False

        def save_config(self, filepath=None):
                """Save configuration to a JSON file."""
                file_to_save = filepath or self.config_file
                try:
                        with open(file_to_save, "w") as f:
                                # Custom formatting to keep arrays on single lines
                                json_str = json.dumps(
                                        self.config, indent=2, ensure_ascii=False
                                )
                                # Compact arrays by removing newlines within them
                                import re

                                # Match arrays and compress them to single lines
                                json_str = re.sub(r"\[\s+", "[", json_str)
                                json_str = re.sub(r"\s+\]", "]", json_str)
                                json_str = re.sub(r",\s+(\d)", r", \1", json_str)
                                f.write(json_str)
                        return True
                except Exception as e:
                        print(f"Error saving config: {e}")
                        return False

        def set_dimensions(self, width, height):
                """Set the puzzle dimensions."""
                old_width = self.config.get("width", 0)
                old_height = self.config.get("height", 0)

                self.config["width"] = width
                self.config["height"] = height

                # Only reset clues if dimensions actually changed
                if old_width != width or old_height != height:
                        # Preserve existing clues and only add missing ones
                        if "rows" not in self.config:
                                self.config["rows"] = {}
                        if "columns" not in self.config:
                                self.config["columns"] = {}

                        # Add missing row entries
                        for i in range(height):
                                if str(i) not in self.config["rows"]:
                                        self.config["rows"][str(i)] = []

                        # Add missing column entries
                        for i in range(width):
                                if str(i) not in self.config["columns"]:
                                        self.config["columns"][str(i)] = []

                        # Remove extra rows if height decreased
                        rows_to_remove = [
                                k
                                for k in self.config["rows"].keys()
                                if int(k) >= height
                        ]
                        for k in rows_to_remove:
                                del self.config["rows"][k]

                        # Remove extra columns if width decreased
                        cols_to_remove = [
                                k
                                for k in self.config["columns"].keys()
                                if int(k) >= width
                        ]
                        for k in cols_to_remove:
                                del self.config["columns"][k]

        def set_row_clue(self, row_index, clues):
                """Set clue for a specific row. clues should be a list of integers."""
                self.config["rows"][str(row_index)] = clues

        def set_column_clue(self, col_index, clues):
                """Set clue for a specific column. clues should be a list of integers."""
                self.config["columns"][str(col_index)] = clues

        def get_row_clue(self, row_index):
                """Get clue for a specific row."""
                return self.config["rows"].get(str(row_index), [])

        def get_column_clue(self, col_index):
                """Get clue for a specific column."""
                return self.config["columns"].get(str(col_index), [])

        def get_dimensions(self):
                """Get puzzle dimensions."""
                return self.config["width"], self.config["height"]

        def get_config(self):
                """Get the entire configuration."""
                return self.config

        def validate_config(self):
                """Validate the configuration."""
                if self.config["width"] < 1 or self.config["height"] < 1:
                        return False, "Dimensions must be at least 1x1"
                return True, "Configuration is valid"
