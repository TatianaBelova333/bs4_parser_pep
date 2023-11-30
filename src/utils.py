import csv
import logging
from http import HTTPStatus
from pathlib import Path
from typing import Iterable, Optional, Union

from bs4 import BeautifulSoup, Tag
from requests import RequestException
from requests_cache import CachedResponse, CachedSession

from exceptions import HTTPStatusCodeError, ParserFindTagException


def get_response(session: CachedSession, url: str) -> Optional[CachedResponse]:
    """
    Send a GET request to the given url and return a CachedResponse instance.

    """
    try:
        response = session.get(url)
        if response.status_code != HTTPStatus.OK:
            raise HTTPStatusCodeError(
                f'Неуспешный статус-код({response.status_code}) для {url}'
            )
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True,
        )
    except HTTPStatusCodeError as err:
        logging.exception(
            err,
            stack_info=True,
        )


def find_tag(
        soup: BeautifulSoup,
        tag: Union[str, list, callable],
        attrs: Optional[dict[str, str]] = None,
        all: bool = False,
) -> Union[Tag, list[Tag], None]:
    """
    Search the parse tree (soup argument) for the given tag with attrs
    and return a Tag instance, a list of Tag instances or None.

    """
    find = {
        False: soup.find,
        True: soup.find_all,
    }
    searched_tag = find[all](tag, attrs=(attrs or {}))

    if searched_tag in (None, []):
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)

    return searched_tag


def make_dir(base_dir: Path, dir_name: str) -> Path:
    """Create a new directory at the given base_dir path with the dir_name."""
    dir = base_dir / dir_name
    dir.mkdir(exist_ok=True)
    return dir


def write_to_csv_file(
        file_path: Path,
        data: Iterable[Iterable],
        log_message: str
):
    """Create and save data into a csv file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(
            file,
            dialect='unix',
            delimiter=';',
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writerows(data)
        logging.info(log_message)


def write_to_zip_file(
        file_path: Path,
        data: Iterable[Iterable],
        log_message: str
):
    """Create and save data into a zip file."""
    with open(file_path, 'wb') as file:
        file.write(data)
        logging.info(log_message)
