import cv2
from requests import post
import json
import time,random
import base64


filename = 'assets/image1.jpg'
image = cv2.imread(filename)
img = cv2.imencode('.jpg',cv2.resize(image,dsize=(600,600),interpolation=cv2.INTER_AREA))[1].tobytes()

filename2 = 'assets/image2.jpg'
image2 = cv2.imread(filename2)
img2 = cv2.imencode('.jpg',cv2.resize(image2,dsize=(600,600),interpolation=cv2.INTER_AREA))[1].tobytes()
a = base64.b64encode(img)
b = base64.b64encode(img2)

c =list(a);
d = list(b)


for i in range(1,100):
 if (i%2) == 0:
     data={'image':c,'rate':{'cpu':random.random(),'gpu':random.random()}}
     post('http://127.0.0.1:5002/data', data={'data': json.dumps(data)})
 else:
     data={'image':d,'rate':{'cpu':random.random(),'gpu':random.random()}}
     post('http://127.0.0.1:5002/data',data={'data':json.dumps(data)})
 time.sleep(1)