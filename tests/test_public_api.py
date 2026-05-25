from __future__ import annotations

import liblaf.logging
from liblaf.logging.filters import LimitsFilter


def test_all_public_names_are_bound() -> None:
    for name in liblaf.logging.__all__:
        assert hasattr(liblaf.logging, name), name


def test_limits_filter_is_exported_from_top_level() -> None:
    assert liblaf.logging.LimitsFilter is LimitsFilter
