"""Tests for spyglass_workshop.utils."""

from spyglass_workshop import utils


def test_schema_prefix_is_string():
    assert isinstance(utils.SCHEMA_PREFIX, str)
    assert len(utils.SCHEMA_PREFIX) > 0
