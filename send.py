import random, time
from requests import post

send = {}
for i in range(0,200):
    send['cpu'] = random.random()
    send['gpu'] = random.random()
    post('http://127.0.0.1:5002/data',data={'rate':str(send)})
    time.sleep(1)