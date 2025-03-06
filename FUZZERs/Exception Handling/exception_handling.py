import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor

# Configuration
base_url = 'http://127.0.0.1:8080'
concurrency = 10  # Number of threads
request_timeout = 5  # Timeout for each request in seconds
delay_between_requests = 0.1  # Delay to handle rate limiting (set to 0 for no delay)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Endpoints to fuzz
endpoints = {
    'login': {
        'fields': ['username', 'password'],
        'method': 'post'
    },
    'signup': {
        'fields': ['username', 'password', 'email'],
        'method': 'post'
    }
}

# Define payloads
general_payloads = [
    '',
    ' ' * 5000,
    None,
    '\'', 
    '"',
    '<script>alert(1)</script>',
    'true',
    'null',
    '{}',
    '[]',
    '\' OR \'1\'=\'1\' --',  # SQL injection
    '../../etc/passwd',     # Path traversal
    '\0',                   # Null byte
    '🤔',                   # Unicode
    'admin',                # Logic bomb
    '100000000000000000000',  # Overflow number
    '-1',                    # Negative number
    '; ls',                  # Command injection (Unix)
    '&& dir',                # Command injection (Windows)
    'O:8:"stdClass":0:{}',  # Basic object injection
    'true',                  # Boolean as a string
    'false'                  # Boolean as a string

]

headers_variants = [
    {},
    {'User-Agent': 'InvalidUserAgent'},
    {'Content-Type': 'text/plain'},
]

session = requests.Session()

def fuzz(endpoint, details):
    """Fuzz an endpoint with malicious or unexpected payloads."""
    url = f'{base_url}/{endpoint}'
    logging.info(f"Fuzzing {url}...")

    for header in headers_variants:
        for payload in general_payloads:
            data = {field: payload for field in details['fields']}

            try:
                if details['method'] == 'post':
                    response = session.post(url, data=data, headers=header, timeout=request_timeout)
                else:
                    response = session.get(url, params=data, headers=header, timeout=request_timeout)

                if "exception" in response.text.lower() or "error" in response.text.lower():
                    logging.warning(f"Possible exception leakage at {url} with payload {payload} and header {header}")
                    logging.warning(f"Response: {response.text}")
                else:
                    logging.info(f"Endpoint {endpoint} handled the payload gracefully.")
                
                time.sleep(delay_between_requests)  # Handle rate limiting

            except Exception as e:
                logging.error(f"Exception occurred for {url} with payload {payload} and header {header}. Error: {str(e)}")

def main():
    """Main function to run the fuzzer."""
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        for endpoint, details in endpoints.items():
            executor.submit(fuzz, endpoint, details)

if __name__ == "__main__":
    main()
