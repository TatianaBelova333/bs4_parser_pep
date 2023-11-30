import logging
from argparse import ArgumentParser
from logging.handlers import RotatingFileHandler
from typing import Sequence

from constants import BASE_DIR

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


def configure_argument_parser(available_modes: Sequence) -> ArgumentParser:
    """Configure arguments for the parser and return it."""
    parser = ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера',
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша',
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных',
    )
    return parser


def configure_logging() -> None:
    """Configer logger."""
    log_dir: str = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file: str = log_dir / 'parser.log'

    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5,
    )

    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
