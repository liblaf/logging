"""Runtime configuration for `liblaf.logging`."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from liblaf import conf

if TYPE_CHECKING:
    from _typeshed import StrPath


def _default_hide_frame() -> list[str]:
    return ["logging", "rich.progress"]


def _field_path_or_none(
    env: str | None = None,
    default: Path | None = None,
    factory: conf.Factory[Path | None] | None = None,
    converter: conf.Converter[Path | None] | None = None,
) -> conf.Field[Path | None]:
    if converter is None:

        def converter(x: StrPath | None) -> Path | None:
            return Path(x) if x is not None else None

    return conf.field(env=env, default=default, factory=factory, converter=converter)


class Config(conf.BaseConfig):
    """Environment-backed logging settings.

    Values are read with the `LOG_` environment prefix. The process-wide
    [`config`][liblaf.logging.config] instance supplies defaults for
    [`init`][liblaf.logging.init], Rich handler timestamps, hidden-frame
    detection, and release-aware traceback or warning filtering.

    Examples:
        >>> settings = Config()
        >>> settings.level.get()
        'INFO'
        >>> settings.file.get() is None
        True

    Attributes:
        datefmt: `strftime` format for absolute timestamps.
        file: Optional path for the default file handler.
        hide_frame: Module-name prefixes skipped for caller attribution.
        hide_stable_release: Whether stable installed code is hidden from Rich
            tracebacks and warning locations.
        level: Default root logging level used by `init`.
        time_relative: Whether default handlers render relative timestamps.
    """

    env_prefix: ClassVar[str] = "LOG_"
    # ref: <https://pendulum.eustace.io/docs/#tokens>
    datefmt: conf.Field[str] = conf.field_str(default="%Y-%m-%d %H:%M:%S%z")
    file: conf.Field[Path | None] = _field_path_or_none(default=None)
    hide_frame: conf.Field[list[str]] = conf.field_list_str(factory=_default_hide_frame)
    hide_stable_release: conf.Field[bool] = conf.field_bool(default=True)
    level: conf.Field[str] = conf.field_str(default="INFO")
    time_relative: conf.Field[bool] = conf.field_bool(default=True)


config: Config = Config()
"""Process-wide logging configuration."""
