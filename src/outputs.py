import datetime as dt
from typing import Iterable

from prettytable import PrettyTable
from tqdm import tqdm

from constants import BASE_DIR, DATETIME_FORMAT, RESULT_DIR
from utils import make_dir, write_to_csv_file


def control_output(results, cli_args):
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results: Iterable):
    """Print the results in the terminal row by row."""
    for row in results:
        print(*row)


def pretty_output(results: Iterable, table_align='l'):
    """Generate a PrettyTable and print it in the terminal."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = table_align
    table.add_rows(results[1:])
    print(table)


def file_output(results: Iterable[Iterable], cli_args):
    """Create a new directory and save data in a csv file in it."""
    file_format = 'csv'
    results_dir = make_dir(dir_name=RESULT_DIR, base_dir=BASE_DIR)

    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)

    file_name = f'{parser_mode}_{now_formatted}.{file_format}'

    file_path = results_dir / file_name
    message = f'Файл с результатами был сохранён: {file_path}'

    tqdm(write_to_csv_file(
        file_path=file_path,
        data=results,
        log_message=message),
        desc='Загрузка результатов в csv-файл'
    )
