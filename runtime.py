"""Runtime execution layer.

Provides a minimal task execution engine that runs registered callables.
The runtime owns "how" to execute tasks; the control-plane owns "what" and "when".
"""

from typing import Any, Callable, Dict, List


_registry: Dict[str, Callable[..., Any]] = {}


def register_task(name: str, func: Callable[..., Any]) -> None:
    """Register a callable task under a unique name.

    Args:
        name: Unique task identifier.
        func: A callable to execute when the task is invoked.

    Raises:
        ValueError: If name is empty or func is not callable.
    """
    if not name or not isinstance(name, str):
        raise ValueError("Task name must be a non-empty string.")
    if not callable(func):
        raise ValueError("Task function must be callable.")
    _registry[name] = func


def list_tasks() -> List[str]:
    """Return the names of all registered tasks in registration order."""
    return list(_registry.keys())


def run_task(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a single registered task by name.

    Args:
        name: The registered task name.
        *args: Positional arguments forwarded to the task callable.
        **kwargs: Keyword arguments forwarded to the task callable.

    Returns:
        The return value of the task callable.

    Raises:
        KeyError: If the task name is not registered.
    """
    if name not in _registry:
        raise KeyError(f"Task '{name}' is not registered.")
    return _registry[name](*args, **kwargs)


def run_all(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Execute every registered task in registration order.

    Args:
        *args: Positional arguments forwarded to every task.
        **kwargs: Keyword arguments forwarded to every task.

    Returns:
        A dict mapping task names to their return values.
    """
    return {name: run_task(name, *args, **kwargs) for name in list_tasks()}
