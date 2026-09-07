"""Migrar class Config: → model_config = ConfigDict(from_attributes=True) en Pydantic schemas."""
import re
from pathlib import Path

SCHEMAS_DIR = Path(r"C:\Proyectos\sistema_gestion_sst\backend\app\schemas")
CONFIG_FILE = Path(r"C:\Proyectos\sistema_gestion_sst\backend\app\config.py")

# Pattern for schemas: class Config:\n    from_attributes = True
SCHEMA_PATTERN = re.compile(
    r'(\n)([ \t]*)(class Config:\n(?:[ \t]+from_attributes = True\n?)+)',
    re.MULTILINE,
)

# Pattern for config.py: class Config: with env_file etc
CONFIG_PATTERN = re.compile(
    r'(\n)([ \t]*)(class Config:\n(?:[ \t]+\w+ = [^\n]+\n?)+)',
    re.MULTILINE,
)


def migrate_schema_file(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8")
    if "class Config:" not in content:
        return False

    # Check if it's the simple from_attributes pattern
    if "from_attributes = True" in content and "class Config:" in content:
        # Add import if not present
        if "from pydantic import ConfigDict" not in content:
            # Add to existing pydantic imports
            content = content.replace(
                "from pydantic import",
                "from pydantic import ConfigDict, ",
                1,
            )
            # Handle case where there are multiple pydantic imports
            if content.count("from pydantic import ConfigDict, ") > 1:
                # Remove duplicate
                content = content.replace(
                    "from pydantic import ConfigDict, from pydantic import ConfigDict, ",
                    "from pydantic import ConfigDict, ",
                )

        # Replace class Config: with model_config = ConfigDict(...)
        content = SCHEMA_PATTERN.sub(
            lambda m: f"{m.group(1)}{m.group(2)}model_config = ConfigDict(from_attributes=True)\n",
            content,
        )

        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def migrate_config_file(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8")
    if "class Config:" not in content:
        return False

    # For Settings class
    if "BaseSettings" in content:
        # Add pydantic_settings import
        if "from pydantic_settings import BaseSettings, SettingsConfigDict" not in content:
            content = content.replace(
                "from pydantic_settings import BaseSettings",
                "from pydantic_settings import BaseSettings, SettingsConfigDict",
            )

        # Extract Config body
        config_match = re.search(
            r'([ \t]*)(class Config:\n(?:[ \t]+\w+ = [^\n]+\n?)+)',
            content,
        )
        if config_match:
            indent = config_match.group(1)
            config_body = config_match.group(2)

            # Parse key = value pairs
            settings = {}
            for line in config_body.split("\n"):
                line = line.strip()
                if line.startswith("class Config:"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    settings[key] = value

            # Build SettingsConfigDict
            config_dict_items = []
            for k, v in settings.items():
                config_dict_items.append(f"{k}={v}")

            config_dict_str = "SettingsConfigDict(" + ", ".join(config_dict_items) + ")"

            # Replace
            content = content[:config_match.start()] + f"{indent}model_config = {config_dict_str}\n" + content[config_match.end():]

            filepath.write_text(content, encoding="utf-8")
            return True
    return False


def main():
    count = 0
    for f in SCHEMAS_DIR.glob("*.py"):
        if migrate_schema_file(f):
            print(f"  OK {f.name}")
            count += 1

    if migrate_config_file(CONFIG_FILE):
        print(f"  OK config.py")
        count += 1

    print(f"\nMigrated {count} files")


if __name__ == "__main__":
    main()
