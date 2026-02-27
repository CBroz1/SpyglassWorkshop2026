"""Tests for channel_stats_buggy helper functions.

These tests target the helper functions that are independent of the three
intentional bugs, so they pass against the buggy module as-is.
"""

import pytest

from spyglass_workshop.channel_stats_buggy import (
    _safe_sqrt,
    _z_scores,
    dummy_function,
)


def test_dummy_function_runs():
    dummy_function([[[1.0, 2.0], [3.0]], [[4.0]]])


def test_safe_sqrt_positive():
    assert _safe_sqrt(4.0) == 2.0
    assert _safe_sqrt(0.0) == 0.0


def test_safe_sqrt_negative_raises():
    with pytest.raises(ValueError, match="variance is negative"):
        _safe_sqrt(-1.0)


def test_z_scores_nonzero_sigma():
    result = _z_scores([1.0, 2.0, 3.0], mu=2.0, sigma=1.0)
    assert result == [-1.0, 0.0, 1.0]


def test_z_scores_zero_sigma_returns_zeros():
    result = _z_scores([5.0, 5.0, 5.0], mu=5.0, sigma=0.0)
    assert result == [0.0, 0.0, 0.0]
