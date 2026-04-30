import urllib.request
import threading
import time

# You will replace this URL after deployment
URL = "http://192.168.59.101:31427/cpu"
THREADS = 20
DURATION = 120  # seconds

def hammer():
    end = time.time() + DURATION
    while time.time() < end:
        try:
            urllib.request.urlopen(URL, timeout=5)
        except:
            pass

print(f"Starting load test — {THREADS} threads for {DURATION} seconds")
threads = [threading.Thread(target=hammer) for _ in range(THREADS)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("Load test complete")