"""Tests for the channel_stats_buggy debugging exercise.

These tests define the *correct* expected behavior.  They will fail
against the buggy module.  Fix the bugs in
``src/spyglass_workshop/channel_stats_buggy.py`` until all tests pass.
"""

import math

import pytest

from spyglass_workshop.channel_stats_buggy import summarize

# All tests in this file are expected to fail until the three bugs in
# channel_stats_buggy.py are fixed.  xfail lets CI pass in the meantime;
# once a test starts passing it is reported as xpass (not a CI failure).
pytestmark = pytest.mark.xfail(
    reason="Intentional bugs in channel_stats_buggy.py — fix all three to pass",
    strict=False,
)


def test_single_sample_channel():
    """A single-sample channel has std=0 and z-score=0.0."""
    result = summarize([[7.0]])[0]
    assert result["mean"] == 7.0
    assert result["std"] == 0.0
    assert result["z_scores"] == [0.0]


def test_flat_channel_z_scores_are_zero():
    """A dead/flat channel should return z-scores of 0.0, not raise."""
    result = summarize([[3.0, 3.0, 3.0, 3.0]])[0]
    assert result["std"] == 0.0
    assert all(z == 0.0 for z in result["z_scores"])


@pytest.mark.parametrize(
    "signal,expected_mean,expected_std",
    [
        ([1.0, 2.0, 3.0, 4.0, 5.0], 3.0, math.sqrt(2.0)),
        ([0.0, 4.0], 2.0, 2.0),
        ([7.0], 7.0, 0.0),
    ],
)
def test_mean_and_std(signal, expected_mean, expected_std):
    result = summarize([signal])[0]
    assert math.isclose(result["mean"], expected_mean, rel_tol=1e-9)
    assert math.isclose(result["std"], expected_std, abs_tol=1e-9)


def test_z_scores_specific_values():
    # [2, 4, 6] → mu=4, population std = sqrt(8/3)
    signal = [2.0, 4.0, 6.0]
    result = summarize([signal])[0]
    expected_std = math.sqrt(8 / 3)
    assert math.isclose(result["std"], expected_std, rel_tol=1e-9)
    assert math.isclose(result["z_scores"][1], 0.0, abs_tol=1e-9)
    assert math.isclose(
        result["z_scores"][0], (2.0 - 4.0) / expected_std, rel_tol=1e-9
    )


def test_multi_channel():
    channels = [[1.0, 2.0, 3.0], [5.0, 5.0, 5.0]]
    result = summarize(channels)
    assert set(result.keys()) == {0, 1}
    assert result[1]["std"] == 0.0
    assert all(z == 0.0 for z in result[1]["z_scores"])
