from bottle import request, response
from bottle import get
import json
import re
from db import *

@get('/employee/:id')
def read_employee(id):
    response.headers['Content-Type'] = 'application/json'
    try:
        document = Employee.objects.get(id=id).to_json()
    except DoesNotExist:
        response.status = 404
        return json.dumps({"res":"Document not found"})
    except ValidationError:
        response.status = 400
        return json.dumps({"res":"Not a valid id"})

    response.status = 200
    return document