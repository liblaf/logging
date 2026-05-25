"""`sys.unraisablehook` integration for logging."""

from __future__ import annotations

import logging
import sys

logger: logging.Logger = logging.getLogger()


def install_unraisablehook(level: int = logging.ERROR) -> None:
    """Install a hook that logs unraisable exceptions.

    Args:
        level: Logging level used when an unraisable exception has an
            `exc_value`.
    """

    def unraisablehook(args: sys.UnraisableHookArgs, /) -> None:
        if args.exc_value is None:
            return
        logger.log(
            level,
            "%s: %r",
            args.err_msg,
            args.object,
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.unraisablehook = unraisablehook
