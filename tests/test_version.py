import packaging.version

import spyglass_workshop


def test_version_is_valid() -> None:
    _ = packaging.version.parse(spyglass_workshop.__version__)
