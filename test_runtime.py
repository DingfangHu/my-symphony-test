"""Tests for runtime.py (standalone execution layer).

Also verifies that the runtime module structurally conforms to
the ``RuntimeInterface`` protocol defined in runtime_interface.py.
"""

import runtime as rt
from runtime_interface import RuntimeInterface


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_modules():
    """Reset mutable module state between tests.

    Directly clears internal dicts so each test starts from a
    clean slate without re-importing.
    """
    rt._registry.clear()


# ---------------------------------------------------------------------------
# Unit tests
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
# Interface conformance
# ---------------------------------------------------------------------------

def test_runtime_conforms_to_interface():
    """Verify the runtime module satisfies RuntimeInterface structurally."""
    # The runtime module must expose all four methods required by the protocol
    assert callable(rt.register_task)
    assert callable(rt.list_tasks)
    assert callable(rt.run_task)
    assert callable(rt.run_all)

    # Verify basic round-trip through the interface contract
    _reset_modules()
    rt.register_task("echo", lambda x: x)
    assert rt.run_task("echo", 42) == 42


def test_runtime_can_be_used_as_interface():
    """Verify the runtime module can be assigned to RuntimeInterface typed var."""
    _reset_modules()
    impl: RuntimeInterface = rt
    impl.register_task("test", lambda: "ok")
    assert impl.run_task("test") == "ok"
    assert impl.list_tasks() == ["test"]
    assert impl.run_all() == {"test": "ok"}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_register_and_list_tasks,
        test_register_empty_name_raises,
        test_register_non_callable_raises,
        test_run_task,
        test_run_task_not_registered,
        test_run_all,
        test_run_all_with_args,
        # interface conformance
        test_runtime_conforms_to_interface,
        test_runtime_can_be_used_as_interface,
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
