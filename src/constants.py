from pathlib import Path
from urllib.parse import urljoin

MAIN_DOC_URL = 'https://docs.python.org/3/'
WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')
DOWNLOADS_URL = urljoin(MAIN_DOC_URL, 'download.html')
PEP_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
RESULT_DIR = 'results'
DOWNLOAD_DIR = 'downloads'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DOWNLOADS_FORMAT = r'pdf-a4\.zip'
EXPECTED_STATUS = {
        'A': ('Active', 'Accepted'),
        'D': ('Deferred',),
        'F': ('Final',),
        'P': ('Provisional',),
        'R': ('Rejected',),
        'S': ('Superseded',),
        'W': ('Withdrawn',),
        '': ('Draft', 'Active'),
    }
OUTPUT_FILE_COLS = {
    'whats_new': ('Ссылка на статью', 'Заголовок', 'Редактор, Автор'),
    'latest_versions': ('Ссылка на документацию', 'Версия', 'Статус'),
    'pep': ('Статус', 'Количество'),
}
