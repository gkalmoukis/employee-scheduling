from bottle import request, response
from bottle import get
import json
import re
from db import *

@get('/employee')
def read_employees():
    response.headers['Content-Type'] = 'application/json'
    response.status = 200
    return Employee.objects.to_json()