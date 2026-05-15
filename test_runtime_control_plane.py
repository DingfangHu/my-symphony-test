"""Tests for runtime.py and control_plane.py."""

import runtime as rt
import control_plane as cp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_modules():
    """Reset mutable module state between tests.

    Directly clears internal dicts/lists so each test starts from a
    clean slate without re-importing.
    """
    rt._registry.clear()
    cp._schedule.clear()


# ---------------------------------------------------------------------------
# runtime.py tests
# ---------------------------------------------------------------------------

def test_register_and_list_tasks():
    _reset_modules()
    rt.register_task("t1", lambda: 1)
    rt.register_task("t2", lambda: 2)
    assert rt.list_tasks() == ["t1", "t2"]


def test_register_empty_name_raises():
    _reset_modules()
    try:
        rt.register_task("", lambda: 1)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_register_non_callable_raises():
    _reset_modules()
    try:
        rt.register_task("x", 42)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_run_task():
    _reset_modules()
    rt.register_task("double", lambda x: x * 2)
    assert rt.run_task("double", 5) == 10


def test_run_task_not_registered():
    _reset_modules()
    try:
        rt.run_task("nope")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_run_all():
    _reset_modules()
    rt.register_task("a", lambda: "A")
    rt.register_task("b", lambda: "B")
    results = rt.run_all()
    assert results == {"a": "A", "b": "B"}


def test_run_all_with_args():
    _reset_modules()
    rt.register_task("add", lambda a, b: a + b)
    rt.register_task("mul", lambda a, b: a * b)
    results = rt.run_all(3, b=4)
    assert results == {"add": 7, "mul": 12}


# ---------------------------------------------------------------------------
# control_plane.py tests
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
# Integration: runtime + control_plane
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
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        # runtime
        test_register_and_list_tasks,
        test_register_empty_name_raises,
        test_register_non_callable_raises,
        test_run_task,
        test_run_task_not_registered,
        test_run_all,
        test_run_all_with_args,
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
