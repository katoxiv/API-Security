import requests
import time
import logging
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(filename='replay_attack_fuzzer.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# The URL of the API you're testing
base_url = 'http://127.0.0.1:8080' 

# The endpoint you're testing
endpoint = '/some_endpoint'

# Delay between requests
delay = 5  # in seconds

# Number of replay attempts
attempts = 5

# Request data
data = {'some_key': 'some_value'}  # this would be the specific data required for the request

# Headers for the request
headers = {'Content-Type': 'application/json'}

def test_replay_attack():
    for attempt in range(attempts):
        logging.info(f'Starting attempt #{attempt+1}')

        # Make the initial request
        initial_response = send_request(data, headers)
            
        # If there's a problem with the initial request, skip the replay attempt
        if initial_response is None:
            logging.warning('Initial request failed, skipping this attempt')
            continue

        # Wait for a certain time
        logging.info(f'Waiting for {delay} seconds before replay attempt')
        time.sleep(delay)

        # Try the request again with the same data and headers
        replay_response = send_request(data, headers)

        # If the replay response matches the initial response, log a warning
        if replay_response is not None and replay_response.status_code == initial_response.status_code and replay_response.text == initial_response.text:
            logging.warning(f'Possible replay attack. The same response received for identical requests.')

def send_request(data, headers):
    try:
        response = requests.post(f'{base_url}{endpoint}', json=data, headers=headers)
        log_response(response)
        return response
    except RequestException as e:
        logging.error(f'Request error: {e}')
        return None

def log_response(response):
    if response is None:
        return
    if response.status_code == 200:
        logging.info(f'Successful request. Status Code: {response.status_code}')
    else:
        logging.warning(f'Non 200 response code: {response.status_code}')
    logging.info(f'Response content: {response.text}')

if __name__ == '__main__':
    test_replay_attack()
