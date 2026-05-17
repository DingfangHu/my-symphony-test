"""Runtime interface contract.

Defines the protocol that any runtime execution layer must implement.
The control-plane depends on this contract, not on a concrete implementation.

This is the formal boundary between the scheduling layer (control-plane)
and the execution layer (runtime).
"""

from typing import Any, Callable, Dict, List, Protocol


class RuntimeInterface(Protocol):
    """Protocol defining the runtime execution layer contract.

    Any object with these four methods satisfies the interface
    via structural subtyping -- no explicit inheritance needed.
    The built-in ``runtime`` module already conforms.
    """

    def register_task(self, name: str, func: Callable[..., Any]) -> None:
        """Register a callable task under a unique name.

        Args:
            name: Unique task identifier.
            func: A callable to execute when the task is invoked.

        Raises:
            ValueError: If name is empty or func is not callable.
        """
        ...

    def list_tasks(self) -> List[str]:
        """Return the names of all registered tasks in registration order."""
        ...

    def run_task(self, name: str, *args: Any, **kwargs: Any) -> Any:
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
        ...

    def run_all(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute every registered task in registration order.

        Args:
            *args: Positional arguments forwarded to every task.
            **kwargs: Keyword arguments forwarded to every task.

        Returns:
            A dict mapping task names to their return values.
        """
        ...
