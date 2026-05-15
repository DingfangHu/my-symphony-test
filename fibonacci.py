"""Fibonacci number computation using an iterative approach.

Provides fibonacci(n: int) -> int that returns the n-th Fibonacci number
in O(n) time and O(1) space. Raises ValueError for negative inputs.
"""


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number (0-indexed).

    Uses an iterative bottom-up approach with O(n) time and O(1) space.

    Args:
        n: A non-negative integer index into the Fibonacci sequence.

    Returns:
        The n-th Fibonacci number.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(10)
        55
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    if n == 0:
        return 0
    if n == 1:
        return 1

    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 fibonacci.py <n>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
    except ValueError:
        print(f"Error: argument must be an integer, got '{sys.argv[1]}'")
        sys.exit(1)

    try:
        result = fibonacci(n)
        print(f"fibonacci({n}) = {result}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
