import requests
from multiprocessing import Pool
from requests.exceptions import RequestException
from fake_useragent import UserAgent
import random
import string
import csv
import time

# The URL you want to fuzz
base_url = 'http://127.0.0.1:8080'  # Replace with your base url
endpoints = ['/login', '/signup', '/user', '/data']  # Replace these with your endpoints

# HTTP methods to test
methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'CONNECT', 'TRACE', 'PATCH']

# Your regular payload
regular_payload = {'username': 'user', 'password': 'password'}

# Instantiate a UserAgent object to generate random user agents
ua = UserAgent()

# CSV file setup
csv_file = open('http_method_fuzzing_results.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['URL', 'HTTP Method', 'Payload', 'Status Code', 'Response'])

# Function to generate random strings
def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

# Fuzzer function
def fuzz_method(args):
    url, method, data = args
    headers = {"User-Agent": ua.random}
    # Add a retry mechanism
    for i in range(1, 6):
        try:
            with requests.Session() as s:
                response = s.request(method, url, json=data, headers=headers, timeout=5)
                csv_writer.writerow([url, method, data, response.status_code, response.text])
                break
        except RequestException as e:
            csv_writer.writerow([url, method, data, 'Error', str(e)])
            # Exponential backoff
            time.sleep(2**i)
        except Exception as e:
            csv_writer.writerow([url, method, data, 'Error', str(e)])

    # Try fuzzing with random data
    if method in ['POST', 'PUT', 'PATCH']:
        fuzz_data = {random_string(): random_string() for _ in range(10)}
        for i in range(1, 6):
            try:
                response = s.request(method, url, json=fuzz_data, headers=headers, timeout=5)
                csv_writer.writerow([url, method, fuzz_data, response.status_code, response.text])
                break
            except RequestException as e:
                csv_writer.writerow([url, method, fuzz_data, 'Error', str(e)])
                time.sleep(2**i)
            except Exception as e:
                csv_writer.writerow([url, method, fuzz_data, 'Error', str(e)])

# Function to generate fuzzing parameters
def fuzz_params():
    for endpoint in endpoints:
        url = f'{base_url}{endpoint}'
        for method in methods:
            data = regular_payload if method in ['POST', 'PUT', 'PATCH'] else None
            yield url, method, data

# Use multiprocessing to speed up fuzzing
def main():
    with Pool() as p:
        p.map(fuzz_method, fuzz_params())
    csv_file.close()

if __name__ == '__main__':
    main()
