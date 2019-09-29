import json
import re
from flask import Flask,request
from flask_restful import Resource,Api
from collections import deque
from waitress import serve
app = Flask(__name__)
api = Api(app)
queue = deque(maxlen=5)


def validation(str):
    exp = re.compile('{ *(\'image\'|\"image\") *: *(.+) *, *(\'rate\'|\"rate\") *: *{ *(\'cpu\'|\"cpu\") *: *(\d+.?\d+) *, *(\'gpu\'|\"gpu\") *: *(\d+.?\d+) *} *}')
    result = exp.match(str)
    if(result):
         return True
    else:
        return False

class Data(Resource):
    def get(self):
        if (len(queue) != 0):
            ra = queue.popleft()
        else:
            ra = '404'
        return {'data': ra}
    def post(self):
        ra = request.form['data']
        if(validation(ra)):
         ra = ra.replace("'","\"")
         ra = json.loads(ra)
         queue.append(ra)
         state = 'ok'
        else:
         state = 'post form error'
        return {'state':state}

api.add_resource(Data,'/data')
if __name__ == '__main__':
    app.run(debug=False, port=5002)