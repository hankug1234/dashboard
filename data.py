import json
import re
from flask import Flask
from flask_restful import Resource,Api,reqparse

app = Flask(__name__)
api = Api(app)
queue = list()
parser = reqparse.RequestParser(); parser.add_argument('rate',type=str);

def validation(str):
    exp = re.compile('{ *(\'cpu\'|\'gpu\') *: *(\d+.?\d+) *, *(\'cpu\'|\'gpu\') *: *(\d+.?\d+) *}')
    result = exp.match(str)
    if(result):
        if(result.group(1)==result.group(3)):
         return False
        else:
         return True
    else:
        return False

class Data(Resource):
    def get(self):
        if (len(queue) != 0):
            ra = queue.pop(0)
        else:
            ra = '404'
        return {'data': ra}
    def post(self):
        arg = parser.parse_args()
        ra = arg['rate']
        if(validation(ra)):
         ra = ra.replace("'","\"")
         ra = json.loads(ra)
         queue.append(ra)
        else:
         ra = 'post form error'
        return {'new_data':ra}

api.add_resource(Data,'/data')
if __name__ == '__main__':
    app.run(debug=False,port=5002)