#!/usr/bin/env python3
"""Fibonacci numbers — buggy version for debugging exercise.

This module contains intentional bugs. Use the VS Code debugger or
``%debug`` in a Jupyter notebook to locate and fix them.

Run the test suite to check your work::

    pytest tests/examples/test_fibonacci_buggy.py -v
"""


def f(n: int) -> int:
    """Return the nth Fibonacci number."""
    a, b = 1, 0
    for _ in range(n):
        a, b = b, a + b
    return a


def f_list(n: int) -> list[int]:
    """Return a list of the first n Fibonacci numbers."""
    out: list[int] = []
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
        out.append(b)
    return out
