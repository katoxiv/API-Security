import requests
import random
import threading
from queue import Queue
import logging
import math

# Setup logging
logging.basicConfig(filename='malformed_fuzzer.log', level=logging.DEBUG)

# The URL of the API you're testing
base_url = 'http://127.0.0.1:8080'

# The endpoint you're testing
endpoint = '/calculate'

# List of operations for the calculator
operations = ['+', '-', '*', '/', 'sqrt', 'log', 'fact', 'sin', 'cos', 'tan']

# Fuzzing inputs
inputs = list(range(-1000, 1001))  # Include integer numbers
inputs += [round(random.uniform(-1000, 1000), 2) for _ in range(1000)]  # Include float numbers
inputs.append(float('inf'))  # Include a very large number
inputs.append(float('-inf'))  # Include a very large negative number
inputs.append(0)  # Include zero (for division by zero cases)
inputs.append('invalid')  # Include non-numeric input
inputs += [1e-200, 1e200]  # Include very small and large numbers for underflow and overflow

# Create a queue for multithreading
queue = Queue()

def simple_calculate(ops, vals):
    result = vals[0]
    for i, op in enumerate(ops):
        try:
            if op == '+':
                result += vals[i+1]
            elif op == '-':
                result -= vals[i+1]
            elif op == '*':
                result *= vals[i+1]
            elif op == '/':
                result /= vals[i+1] if vals[i+1] != 0 else float('inf')
            elif op == 'sqrt':
                result = math.sqrt(result) if result >= 0 else float('nan')
            elif op == 'log':
                result = math.log(result) if result > 0 else float('-inf')
            elif op == 'fact':
                result = math.factorial(result) if result >= 0 and isinstance(result, int) else float('nan')
            elif op in ['sin', 'cos', 'tan']:
                result = getattr(math, op)(result)
        except ValueError:
            result = float('nan')
    return result

def fuzz_calculator():
    while not queue.empty():
        item = queue.get()
        operations, inputs = item

        data = {"inputs": inputs, "operations": operations}

        try:
            # Send the request
            response = requests.post(f'{base_url}{endpoint}', json=data)

            # If the HTTP status code indicates an error, or the calculated result is incorrect
            # Log the input data
            calculated_result = simple_calculate(operations, inputs)
            if response.status_code != 200 or math.isclose(response.json().get('result', 0), calculated_result, rel_tol=1e-5):
                logging.error(f'Faulty calculation: Inputs: {inputs}, Operations: {operations}, Endpoint: {endpoint}')

        except Exception as e:
            logging.error(f'Error during request: {str(e)}')

        finally:
            queue.task_done()

def start_fuzzer(threads):
    # Fill up the queue with inputs and operations
    for _ in range(1000):  # Adjust this for how many tests you want to run
        random_inputs = random.choices(inputs, k=random.randint(2, 10))
        random_op_seq = random.choices(operations, k=len(random_inputs)-1)
        queue.put((random_op_seq, random_inputs))

    # Start the threads
    for i in range(threads):
        worker = threading.Thread(target=fuzz_calculator)
        worker.start()

    queue.join()

if __name__ == '__main__':
    start_fuzzer(5)
