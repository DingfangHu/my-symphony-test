"""Tests for control_plane.py (scheduling & dispatch layer).

These tests exercise the control-plane scheduling and dispatch logic.
Integration tests verify that the control-plane correctly delegates
execution to the runtime layer, including when the runtime is swapped.
"""

import runtime as rt
import control_plane as cp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_modules():
    """Reset mutable module state between tests.

    Directly clears internal dicts/lists and restores the default runtime
    binding so each test starts from a clean slate.
    """
    rt._registry.clear()
    cp._schedule.clear()
    cp.set_runtime(rt)


# ---------------------------------------------------------------------------
# Control-plane tests
# ---------------------------------------------------------------------------

def test_schedule_and_queue():
    _reset_modules()
    cp.schedule("hello", lambda: "world")
    assert cp.get_queue() == ["hello"]


def test_schedule_empty_name_raises():
    _reset_modules()
    try:
        cp.schedule("", lambda: 1)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_schedule_non_callable_raises():
    _reset_modules()
    try:
        cp.schedule("x", "not_callable")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_dispatch():
    _reset_modules()
    cp.schedule("echo", lambda x: x)
    cp.schedule("square", lambda x: x * x)
    results = cp.dispatch(3)
    assert results == {"echo": 3, "square": 9}


def test_dispatch_preserves_order():
    _reset_modules()
    cp.schedule("first", lambda: 1)
    cp.schedule("second", lambda: 2)
    cp.schedule("third", lambda: 3)
    results = cp.dispatch()
    # dispatch returns a dict, but Python 3.7+ preserves insertion order
    assert list(results.keys()) == ["first", "second", "third"]


def test_clear():
    _reset_modules()
    cp.schedule("x", lambda: 1)
    cp.clear()
    assert cp.get_queue() == []
    # Tasks already registered in runtime should still be there
    assert rt.list_tasks() == ["x"]


# ---------------------------------------------------------------------------
# Integration: control_plane + runtime
# ---------------------------------------------------------------------------

def test_control_plane_uses_runtime():
    """Verify control-plane delegates actual execution to the runtime."""
    _reset_modules()
    cp.schedule("greet", lambda name: f"hi {name}")
    assert cp.dispatch("Alice") == {"greet": "hi Alice"}

    # The same task can also be run directly from runtime
    assert rt.run_task("greet", "Bob") == "hi Bob"


def test_clear_then_reschedule():
    _reset_modules()
    cp.schedule("a", lambda: 1)
    cp.clear()
    cp.schedule("b", lambda: 2)
    assert cp.dispatch() == {"b": 2}


# ---------------------------------------------------------------------------
# Runtime injection tests
# ---------------------------------------------------------------------------

class _MockRuntime:
    """Minimal runtime implementation satisfying RuntimeInterface."""

    def __init__(self):
        self._tasks = {}
        self._calls = []

    def register_task(self, name, func):
        self._tasks[name] = func
        self._calls.append(("register", name))

    def list_tasks(self):
        return list(self._tasks.keys())

    def run_task(self, name, *args, **kwargs):
        self._calls.append(("run", name))
        return self._tasks[name](*args, **kwargs)

    def run_all(self, *args, **kwargs):
        return {n: self.run_task(n, *args, **kwargs) for n in self.list_tasks()}


def test_get_runtime_defaults_to_builtin():
    _reset_modules()
    runtime = cp.get_runtime()
    # The default runtime should have the standard register_task / run_task
    assert hasattr(runtime, "register_task")
    assert hasattr(runtime, "run_task")
    assert hasattr(runtime, "list_tasks")
    assert hasattr(runtime, "run_all")


def test_set_and_get_runtime():
    _reset_modules()
    mock = _MockRuntime()
    cp.set_runtime(mock)
    assert cp.get_runtime() is mock


def test_dispatch_uses_injected_runtime():
    _reset_modules()
    mock = _MockRuntime()
    cp.set_runtime(mock)

    cp.schedule("double", lambda x: x * 2)
    cp.schedule("triple", lambda x: x * 3)

    results = cp.dispatch(4)
    assert results == {"double": 8, "triple": 12}
    # Verify the mock runtime received the expected calls
    assert mock._calls[0] == ("register", "double")
    assert mock._calls[1] == ("register", "triple")
    assert mock._calls[2] == ("run", "double")
    assert mock._calls[3] == ("run", "triple")


def test_injected_runtime_preserves_schedule_independence():
    """Swapping the runtime does not affect the control-plane's own schedule."""
    _reset_modules()
    mock = _MockRuntime()
    cp.set_runtime(mock)
    cp.schedule("a", lambda: 1)
    assert cp.get_queue() == ["a"]
    # The built-in runtime's registry should be untouched
    assert rt.list_tasks() == []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        # control_plane
        test_schedule_and_queue,
        test_schedule_empty_name_raises,
        test_schedule_non_callable_raises,
        test_dispatch,
        test_dispatch_preserves_order,
        test_clear,
        # integration
        test_control_plane_uses_runtime,
        test_clear_then_reschedule,
        # runtime injection
        test_get_runtime_defaults_to_builtin,
        test_set_and_get_runtime,
        test_dispatch_uses_injected_runtime,
        test_injected_runtime_preserves_schedule_independence,
    ]

    failures = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
        except Exception as exc:
            failures += 1
            print(f"  FAIL  {test.__name__}: {exc}")

    print(f"\n{len(tests)} tests, {failures} failure(s)")
    if failures:
        raise SystemExit(1)
