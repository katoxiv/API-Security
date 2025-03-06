import asyncio
import aiohttp
import random
import logging
from aiohttp import ClientSession, ClientError
from contextlib import asynccontextmanager
import csv
import time

# The URL of the API you're testing
base_url = 'http://127.0.0.1:8080'

# The endpoints you're testing
endpoints = ['/calculate', '/login', '/signup']

# List of operations for the calculator
operations = ['+', '-', '*', '/', '']

# Fuzzing inputs
inputs = list(range(-1000, 1001))

# Set up logging
logging.basicConfig(filename='dos_fuzz.log', level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')

random.seed(1) # Provide a seed for reproducible results

@asynccontextmanager
async def get_writer(file_path):
    file = open(file_path, 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(["Inputs", "Operation", "Endpoint", "Response Time", "Status Code", "Response Text"])
    try:
        yield writer
    finally:
        file.close()

async def stress_test(session: ClientSession, operation: str, inputs: list, endpoint: str, sem: asyncio.Semaphore, writer: csv.writer):
    async with sem:
        data = {"inputs": inputs, "operation": operation}
        try:
            start_time = time.time()
            async with session.post(f'{base_url}{endpoint}', json=data) as response:
                end_time = time.time()
                response_time = end_time - start_time
                status = response.status
                response_text = await response.text()

                if 200 <= status < 300: # check if status code is in expected range
                    logging.info(f'Successful calculation: Inputs: {inputs}, Operation: {operation}, Endpoint: {endpoint}, Response: {response_text}, Time: {response_time} seconds')
                else:
                    logging.error(f'Faulty calculation: Inputs: {inputs}, Operation: {operation}, Endpoint: {endpoint}, Response: {response_text}')

                writer.writerow([inputs, operation, endpoint, response_time, status, response_text])
        except (ClientError, TimeoutError) as e:
            logging.error(f'Network error: {str(e)}')

async def run(number_of_tests: int, number_of_connections: int, writer: csv.writer):
    logging.info(f'Starting test run with {number_of_tests} tests and {number_of_connections} concurrent connections.')
    sem = asyncio.Semaphore(number_of_connections)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(number_of_tests):
            operation = random.choice(operations)
            inputs_values = random.choices(inputs, k=random.randint(1, 3))
            endpoint = random.choice(endpoints)
            tasks.append(stress_test(session, operation, inputs_values, endpoint, sem, writer))
        await asyncio.gather(*tasks)
    logging.info(f'Test run finished.')

async def main():
    async with get_writer('dos_fuzz.csv') as writer:
        await run(5000, 1000, writer)

if __name__ == '__main__':
    asyncio.run(main())
