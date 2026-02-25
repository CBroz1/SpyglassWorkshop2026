"""Test that the version string is valid."""

import packaging.version

import spyglass_workshop


def test_version_is_valid() -> None:
    """Test that the version string is valid."""
    _ = packaging.version.parse(spyglass_workshop.__version__)
