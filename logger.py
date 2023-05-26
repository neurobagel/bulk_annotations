import logging

from rich.logging import RichHandler


def bulk_annotation_logger(log_level: str = "INFO"):
    FORMAT = "%(message)s"

    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    return logging.getLogger("rich")
