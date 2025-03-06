import httpx
import logging
import random
import asyncio
import time
from itertools import product

# Configure logging
logging.basicConfig(filename='http_testing.log', level=logging.INFO)

# Define the base URL, endpoints, HTTP versions, methods, headers, and payloads
base_url = 'http://127.0.0.1:8080'
endpoints = ['/login', '/calculate', '/signup']
http_versions = ["HTTP/1.1", "HTTP/2"]
http_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"]

headers = [
    {"Accept": "text/html"},
    {"Accept-Encoding": "gzip, deflate, br"},
    {"Content-Type": "application/json"},
    {"Content-Type": "application/xml"},
    {"Content-Type": "' OR '1'='1"}
]

payloads = ['string', '!@#$', '\'', '\"', 'True', 'None', str("A"*6000), 123, True, False, {"key": "value"}, ["item1", "item2"], "' OR '1'='1", "SELECT * FROM users"]

# Define the fuzzing function
async def fuzz_http_versions(endpoint, version, method, header, payload):
    async with httpx.AsyncClient(http2=version == "HTTP/2", headers=header) as client:
        try:
            start_time = time.time()
            response = await client.request(method, f'{base_url}{endpoint}', data=payload)
            end_time = time.time()
            logging.info(f'Response time: {end_time - start_time} seconds')
            logging.info(f'Successful response from {endpoint} using {version} with method {method}. Status Code: {response.status_code}')
            if response.status_code != 200:
                logging.warning(f'Non 200 response code: {response.status_code}')
        except Exception as e:
            logging.error(f'Error hitting {endpoint} using {version} with method {method}: {e}')

# Define the main function
async def main():
    # Shuffle the list to introduce randomness
    random.shuffle(endpoints)
    random.shuffle(http_versions)
    random.shuffle(http_methods)
    random.shuffle(headers)
    random.shuffle(payloads)

    # Use asynchronous tasks for fuzzing
    tasks = []

    for endpoint, version, method, header, payload in product(endpoints, http_versions, http_methods, headers, payloads):
        tasks.append(fuzz_http_versions(endpoint, version, method, header, payload))

    await asyncio.gather(*tasks)

# Run the fuzzer
if __name__ == '__main__':
    asyncio.run(main())
