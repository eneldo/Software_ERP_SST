"""
Import all model modules in this package so SQLAlchemy mappers
are configured correctly regardless of import order elsewhere.

This dynamically imports every module in the `app.models` package
on package import, ensuring classes like `Empresa` are registered
before other models that reference them by string name.
"""
import importlib
import pkgutil
from pathlib import Path


def import_all_models() -> list[str]:
    """Import every model module in this package and return their names."""
    package_name = __name__
    package_path = Path(__file__).resolve().parent
    imported_modules: list[str] = []

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        if module_name.startswith("_") or module_name == "__init__":
            continue

        importlib.import_module(f"{package_name}.{module_name}")
        imported_modules.append(module_name)

    return imported_modules


__all__ = import_all_models()