# Auth module
import importlib.util
import sys
from pathlib import Path

# Register dot-named modules so they can be imported as app.modules.auth.auth.*
_auth_dir = Path(__file__).parent

# List of dot-named modules to register (order matters - dependencies first)
_auth_modules = [
    "schema",      # No dependencies on other auth.* modules
    "repository",  # No dependencies on other auth.* modules
    "utils",       # Depends on repository
    "service",     # Depends on repository, utils
    "router"       # Depends on service, schema
]

# First pass: Register all modules in sys.modules (without executing)
_modules = {}
for module_name in _auth_modules:
    module_file = _auth_dir / f"auth.{module_name}.py"
    if module_file.exists():
        spec = importlib.util.spec_from_file_location(
            f"app.modules.auth.auth.{module_name}",
            module_file
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"app.modules.auth.auth.{module_name}"] = module
            _modules[module_name] = (spec, module)

# Second pass: Execute modules in dependency order
for module_name in _auth_modules:
    if module_name in _modules:
        spec, module = _modules[module_name]
        spec.loader.exec_module(module)
