import importlib


def python_module_exists(module_name: str) -> bool:
    spam_spec = importlib.util.find_spec(module_name)
    return spam_spec is not None
