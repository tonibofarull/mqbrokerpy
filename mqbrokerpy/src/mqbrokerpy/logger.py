import logging


def configure_logger(level) -> None:
    logging.basicConfig(
        format="[%(filename)s:%(lineno)d] %(levelname)s - %(message)s",
        level=level,
    )
