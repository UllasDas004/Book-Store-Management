import httpx
import time

url = "http://127.0.0.1:8000/books/"
print(f"Testing Rate Limit on {url} (Allowed: 60/min)")

success_count = 0
with httpx.Client() as client:
    for i in range(1, 65):
        try:
            response = client.get(url)
            if response.status_code == 200:
                success_count += 1
                if i % 10 == 0:
                    print(f"Request {i}: Status 200 OK")
            elif response.status_code == 429:
                print(f"Request {i}: Status {response.status_code}")
                print(f"✅ RATE LIMIT SUCCESSFULLY CAUGHT AT REQUEST {i}!")
                break
            else:
                print(f"Request {i}: Status {response.status_code}")
        except Exception as e:
            print(f"Request {i} failed: {e}")
            
print(f"Total Successful Requests Before Block: {success_count}")
