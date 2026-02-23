"""Tests for the fibonacci_buggy debugging exercise.

These tests define the *correct* expected behaviour. They will fail
against the buggy module. Fix the bugs in
``src/spyglass_workshop/examples/fibonacci_buggy.py`` until all
tests pass.
"""

import pytest

from spyglass_workshop.examples import fibonacci_buggy


@pytest.mark.parametrize(
    "n,expected",
    [
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 3),
        (5, 5),
        (6, 8),
        (10, 55),
    ],
)
def test_f(n: int, expected: int) -> None:
    assert fibonacci_buggy.f(n) == expected


@pytest.mark.parametrize(
    "n,expected",
    [
        (1, [1]),
        (2, [1, 1]),
        (5, [1, 1, 2, 3, 5]),
        (8, [1, 1, 2, 3, 5, 8, 13, 21]),
    ],
)
def test_f_list(n: int, expected: list[int]) -> None:
    assert fibonacci_buggy.f_list(n) == expected
