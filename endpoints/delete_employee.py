from bottle import request, response
from bottle import delete
import json
import re
from db import *

@delete('/employee/:id')
def delete_emplolyee(id):
    response.headers['Content-Type'] = 'application/json'
    try:
        Employee.objects.get(id=id).delete()
    except DoesNotExist:
        response.status = 404
        return json.dumps({"res":"Document not found"})
    except ValidationError:
        response.status = 406
        return json.dumps({"res":"Not a valid id"})

    response.status = 200
    return json.dumps({"res":"Document deleted"})