"""Rich process configuration."""

import rich


def setup_rich() -> None:
    """Configure Rich to write to stderr by default."""
    rich.reconfigure(stderr=True)
