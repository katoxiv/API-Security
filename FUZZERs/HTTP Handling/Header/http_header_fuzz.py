import requests
import threading
import logging
from queue import Queue
from requests.exceptions import RequestException
from itertools import product
import time
import json
import random
from logging.handlers import RotatingFileHandler


# The URL of the API you're testing
base_url = 'http://127.0.0.1:8080'

# The endpoint you're testing
endpoint = '/calculate'

# Generate a list of fuzzing payloads
payloads = ['string', '!@#$', '\'', '\"', 'True', 'None', str("A"*6000), 123, True, False, {"key": "value"}, ["item1", "item2"]]

# List of HTTP methods to fuzz
methods = ["GET", "POST", "PUT", "DELETE"]

# List of potential error messages indicating a security issue
error_messages = ["error", "exception", "traceback", "invalid"]

# Fuzzing HTTP headers
headers = [
    {"Accept": "text/html"},
    {"Accept-Encoding": "gzip, deflate, br"},
    {"Accept-Language": "en-US,en;q=0.5"},
    {"Cache-Control": "max-age=0"},
    {"Connection": "keep-alive"},
    {"Content-Encoding": "gzip"},
    {"Content-Length": "100"},
    {"Content-Type": "application/x-www-form-urlencoded"},
    {"Cookie": "id=a3fWa; Expires=Thu, 21 Oct 2023 07:28:00 GMT; Secure; HttpOnly"},
    {"DNT": "1"},
    {"Host": "localhost"},
    {"Origin": "http://127.0.0.1:8080"},
    {"Pragma": "no-cache"},
    {"Referer": "http://127.0.0.1:8080"},
    {"TE": "Trailers"},
    {"Transfer-Encoding": "chunked"},
    {"Upgrade-Insecure-Requests": "1"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"},
    {"Via": "1.1 google"},
    {"Warning": "199 Miscellaneous warning"},
    {"X-Content-Type-Options": "nosniff"},
    {"X-Forwarded-For": "123.123.123.123"},
    {"X-Forwarded-Host": "localhost"},
    {"X-Forwarded-Proto": "https"},
    {"X-Frame-Options": "SAMEORIGIN"},
    {"X-Powered-By": "Express"},
    {"X-Requested-With": "XMLHttpRequest"},
    {"X-XSS-Protection": "1; mode=block"},
    {"Content-Security-Policy": "default-src 'none'"},
    {"Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"}
]

user_agents = ['Mozilla/5.0', 'MSIE 9.0', 'Opera/9.80']

queue = Queue()
rate_limit = threading.BoundedSemaphore(value=5)  # requests per second
sleep_interval = 0.2  # seconds

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('http_header_fuzzer.log', maxBytes=10000, backupCount=3)
logger.addHandler(handler)


def fuzz_exceptions(item):
    payload, method, header, user_agent = item
    header['User-Agent'] = user_agent

    data = {"input": payload}
    session = requests.Session()
    req = requests.Request(method, f'{base_url}{endpoint}', headers=header, data=json.dumps(data))
    prepped = req.prepare()

    try:
        rate_limit.acquire()
        start_time = time.time()
        response = session.send(prepped)
        end_time = time.time()
        logger.info(f'Response time: {end_time - start_time} seconds')
    except RequestException as e:
        logger.error(f'Error during request: {str(e)}')
        return
    finally:
        rate_limit.release()
        time.sleep(sleep_interval)

    if response.status_code == 500 or any(err in response.text for err in error_messages):
        logger.info(f'Potentially vulnerable to exceptions - Payload: {payload}, Method: {method}, Endpoint: {endpoint}')
    else:
        logger.info(f'Not vulnerable to exceptions - Payload: {payload}, Method: {method}, Endpoint: {endpoint}')


def start_fuzzer(threads):
    # Shuffle the list to introduce randomness
    random.shuffle(payloads)
    random.shuffle(methods)
    random.shuffle(headers)
    random.shuffle(user_agents)

    for item in product(payloads, methods, headers, user_agents):
        queue.put(item)

    for i in range(threads):
        worker = threading.Thread(target=consume_queue)
        worker.start()

    queue.join()

def consume_queue():
    while not queue.empty():
        item = queue.get()
        fuzz_exceptions(item)
        queue.task_done()

if __name__ == '__main__':
    start_fuzzer(5)