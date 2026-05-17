"""Control-plane scheduling layer.

Manages the task queue and dispatches scheduled tasks to the runtime for actual
execution.  The control-plane owns "what" and "when"; the runtime owns "how".

The control-plane depends on the ``RuntimeInterface`` protocol rather than a
concrete runtime implementation.  This lets callers swap in alternative runtimes
for testing or extension.
"""

from typing import Any, Callable, Dict, List

from runtime_interface import RuntimeInterface

import runtime as rt


_schedule: List[str] = []

# The runtime binding used by schedule() and dispatch().
# Defaults to the built-in ``runtime`` module but can be swapped via set_runtime().
_runtime: RuntimeInterface = rt


def set_runtime(impl: RuntimeInterface) -> None:
    """Replace the runtime implementation used for task execution.

    Args:
        impl: Any object satisfying the ``RuntimeInterface`` protocol.
    """
    global _runtime
    _runtime = impl


def get_runtime() -> RuntimeInterface:
    """Return the currently bound runtime implementation."""
    return _runtime


def schedule(name: str, task_func: Callable[..., Any]) -> None:
    """Schedule a task for later dispatch.

    Registers the task with the runtime and adds it to the dispatch queue.

    Args:
        name: Unique task identifier.
        task_func: The callable to associate with the task name.

    Raises:
        ValueError: If name is empty or task_func is not callable.
    """
    if not name or not isinstance(name, str):
        raise ValueError("Task name must be a non-empty string.")
    if not callable(task_func):
        raise ValueError("Task function must be callable.")

    _runtime.register_task(name, task_func)
    _schedule.append(name)


def get_queue() -> List[str]:
    """Return the current dispatch queue (task names in scheduled order)."""
    return list(_schedule)


def dispatch(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Dispatch all scheduled tasks to the runtime and return results.

    Args:
        *args: Positional arguments forwarded to every task.
        **kwargs: Keyword arguments forwarded to every task.

    Returns:
        A dict mapping task names to their return values, in scheduled order.
    """
    results: Dict[str, Any] = {}
    for name in list(_schedule):
        results[name] = _runtime.run_task(name, *args, **kwargs)
    return results


def clear() -> None:
    """Clear the dispatch queue (does not unregister from runtime)."""
    _schedule.clear()
