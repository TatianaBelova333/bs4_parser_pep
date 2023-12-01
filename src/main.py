import logging
import re
from collections import Counter
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from requests_cache import CachedResponse, CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOAD_DIR, DOWNLOADS_FORMAT, DOWNLOADS_URL,
                       EXPECTED_STATUS, MAIN_DOC_URL, OUTPUT_FILE_COLS,
                       PEP_URL, WHATS_NEW_URL)
from outputs import control_output
from utils import find_tag, get_response, make_dir, write_to_zip_file


def whats_new(session: CachedSession, url=WHATS_NEW_URL):
    columns: tuple = OUTPUT_FILE_COLS[whats_new.__name__]

    response: Optional[CachedResponse] = get_response(
        session=session,
        url=url,
    )

    if response is None:
        return

    soup: BeautifulSoup = BeautifulSoup(response.text, features='lxml')

    main_div: Optional[Tag] = find_tag(
        soup=soup,
        tag='section',
        attrs={'id': 'what-s-new-in-python'},
    )
    div_with_ul: Optional[Tag] = find_tag(
        soup=main_div,
        tag='div',
        attrs={'class': 'toctree-wrapper'},
    )
    sections_by_python: list = find_tag(
        soup=div_with_ul,
        tag='li',
        attrs={'class': 'toctree-l1'},
        all=True,
    )

    results: list[tuple] = [columns]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(soup=section, tag='a')
        href = version_a_tag['href']
        version_link = urljoin(WHATS_NEW_URL, href)

        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')

        h1 = find_tag(soup=soup, tag='h1')
        dl = find_tag(soup=soup, tag='dl')

        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session: CachedSession, url=MAIN_DOC_URL):
    columns: tuple = OUTPUT_FILE_COLS[latest_versions.__name__]

    response = get_response(session=session, url=url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(
        soup=soup,
        tag='div',
        attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results: list[tuple] = [columns]

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        result = re.search(pattern, a_tag.text)
        if result:
            version, status = result.group('version', 'status')
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))

    return results


def download(
        session: CachedSession,
        url: str = DOWNLOADS_URL,
        download_format: str = DOWNLOADS_FORMAT,
        ) -> None:

    response = get_response(session=session, url=url)

    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    table_tag = find_tag(
        soup=soup,
        tag='table',
        attrs={'class': 'docutils'}
    )

    pdf_a4_tag = find_tag(
        soup=table_tag,
        tag='a',
        attrs={'href': re.compile(fr'.+{download_format}$')}
    )
    pdf_a4_link = pdf_a4_tag['href']

    archive_url = urljoin(url, pdf_a4_link)

    filename = archive_url.split('/')[-1]

    downloads_dir = make_dir(base_dir=BASE_DIR, dir_name=DOWNLOAD_DIR)
    archive_path = downloads_dir / filename

    response = get_response(session=session, url=archive_url)

    tqdm(write_to_zip_file(
        file_path=archive_path,
        data=response.content,
        log_message=f'Архив был загружен и сохранён: {archive_path}'),
        desc='Загрузка результатов в архив'
    )


def pep(
        session: CachedSession,
        url: str = PEP_URL,
        expected_statuses: dict[str, tuple[str]] = EXPECTED_STATUS,
) -> None:
    columns: tuple = OUTPUT_FILE_COLS[pep.__name__]
    results: list[tuple] = [columns]
    counter = Counter()
    response = get_response(session=session, url=url)

    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    num_idx_sect = find_tag(
        soup=soup,
        tag='section',
        attrs={'id': 'numerical-index'},
    )
    num_idx_table = find_tag(
        soup=num_idx_sect,
        tag='table',
    )
    num_idx_table_body = find_tag(
        soup=num_idx_table,
        tag='tbody',
    )
    num_idx_table_rows = find_tag(
        soup=num_idx_table_body,
        tag='tr',
        all=True,
    )
    for row in tqdm(num_idx_table_rows, desc='Загрузка статусов PEP'):
        type_status = find_tag(
            soup=row,
            tag='td',
        ).string

        expected_sts_abbr = type_status[1:]
        expected_sts_full = expected_statuses.get(expected_sts_abbr)

        pep_link_a_tag = find_tag(
            soup=row,
            tag='a',
            attrs={'href': re.compile(r'^pep-\d+/')}
        )
        pep_link = pep_link_a_tag['href']
        pep_url = urljoin(url, pep_link)
        response = get_response(session=session, url=pep_url)
        soup = BeautifulSoup(response.text, features='lxml')
        dl_tag = find_tag(soup=soup, tag='dl')
        dt_status_tag = find_tag(
            soup=dl_tag,
            tag=lambda tag: tag.name == 'dt' and 'Status' in tag.text,
        )
        dd_actual_status = dt_status_tag.find_next_sibling().text
        counter.update({dd_actual_status: 1})

        if expected_sts_full is None:
            logging.info(
                    f"Неизвестная аббревиатура статуса. "
                    f"{pep_url}"
                    f"Статус на главной старанице: {expected_sts_abbr}. "
                    f"Статус в карточке: {dd_actual_status}."
                )
        elif dd_actual_status not in expected_sts_full:
            logging.info(
                    f"Несовпадающие статусы: "
                    f"{pep_url}"
                    f"Статус в карточке: {dd_actual_status} "
                    f"Ожидаемые статусы: {expected_sts_full}"
                )
    results.extend(sorted(counter.items()))

    all_peps_count = sum(counter.values())
    results.append(('TOTAL', all_peps_count))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()

    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f'Аргументы командной строки: {args}')
    session = CachedSession()

    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
