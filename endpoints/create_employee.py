from bottle import request, response
from bottle import post
import json
import re
from db import * 
from passlib.hash import pbkdf2_sha256

@post('/create_employee')
def create_document():
    ret_message = ""
    val_errors = []    
    try:
        try:
            data = request.json
            # print(data)
        except:
            ret_message = "bad json format"
            raise ValueError
        if data is None: 
            ret_message = "data is None"
            raise KeyError

        # todo: overflow check

        # extract and validate name
        keys = {'name' : '[a-zA-Z0-9]+' , 
                'email':'[^@]+@[^@]+\.[^@]+', 
                'password' : '[A-Za-z0-9@#$%^&+=]{8,}', 
                'role':'^[-+]?[0-9]+$'
        }

        for key , val in keys.items():
            if not ( (key in data) and (re.match(val, data[key])) ):
                val_errors.append("in "+key)
                
        if len(val_errors) != 0:
            ret_message = "body error(s)"
            raise ValueError

        # for key, val in data.items():
        #     print(key+" : " +val)
        
        # generate new salt, and hash a password
        hash = pbkdf2_sha256.hash(data['password'])
        # print(hash)

        # Create a new employee
        new_employee = Employee( name = data['name'], email = data['email'], role = data['role'], password = hash)
        new_employee.save()
        
        # return 201 Success
        response.headers['Content-Type'] = 'application/json'
        response.status = 201
        return json.dumps({"message" : "Document created"})

    except ValueError:
        response.status = 400
        if len(val_errors) != 0:
         return json.dumps({"message":ret_message , "erros":val_errors}) 
        
        return json.dumps({"message" : ret_message})

    except KeyError:
        response.status = 400
        return json.decoder({"message" : ret_message})
