"""Logging setup."""
from __future__ import annotations

import logging


def configure_logging() -> None:
    """Configure basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
