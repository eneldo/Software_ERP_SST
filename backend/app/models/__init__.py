"""
Import all model modules in this package so SQLAlchemy mappers
are configured correctly regardless of import order elsewhere.

This dynamically imports every module in the `app.models` package
on package import, ensuring classes like `Empresa` are registered
before other models that reference them by string name.
"""
import pkgutil
import importlib
from pathlib import Path

# Import every module in this package (except __init__.py)
package_name = __name__
package_path = Path(__file__).resolve().parent
for finder, name, ispkg in pkgutil.iter_modules([str(package_path)]):
	if name == "__init__":
		continue
	importlib.import_module(f"{package_name}.{name}")