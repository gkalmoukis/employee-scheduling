from bottle import request, response
from bottle import post, get, put, delete
from db import *
from passlib.hash import pbkdf2_sha256
import json
import re

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

@get('/employee/:id')
def read_employee(id):
    response.headers['Content-Type'] = 'application/json'
    try:
        document = Employee.objects.get(id=id).to_json()
    except DoesNotExist:
        response.status = 404
        return json.dumps({"res":"Document not found"})
    except ValidationError:
        response.status = 406
        return json.dumps({"res":"Not a valid id"})

    response.status = 200
    return document

@get('/employee')
def read_employees():
    response.headers['Content-Type'] = 'application/json'
    response.status = 200
    return Employee.objects.to_json()

@post('/employee')
def create_employee():
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
        keys= {'name' : '[a-zA-Z0-9]+' , 'email':'[^@]+@[^@]+\.[^@]+', 
        'password' : '[A-Za-z0-9@#$%^&+=]{8,}', 'role':'^[-+]?[0-9]+$'}

        for key , val in keys.items():
            if not ( (key in data) and (re.match(val, data[key])) ):
                val_errors.append("in "+key)
                
        if len(val_errors) != 0:
            ret_message = "validate error(s)"
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

@put('/contract/:id')
def update_contract(id):
    ret_message = ""
    val_errors = []
    try:
        try:
            req_employee = Employee.objects.get(id=id)
        except DoesNotExist:
            ret_message = "Document not found"
            raise DoesNotExist
        except ValidationError:
            ret_message = "Not a valid id"
            raise ValidationError
            
        try:
            data = request.json
            # print(data)
        except:
            ret_message = "Bad json format"
            raise ValueError
        if data is None: 
            ret_message = "Data is None"
            raise KeyError
    
        # todo: overflow check
    
        # extract and validate name
        keys= {
            'max_assigns':'^[0-9]+$',
            'min_assigns':'^[0-9]+$',
            'max_cons_wdays':'^[0-9]+$',
            'min_cons_wdays':'^[0-9]+$',
            'max_cons_daysoff':'^[0-9]+$',
            'min_cons_daysoff':'^[0-9]+$',
            'max_cons_weekends':'^[0-9]+$',
            'daysoff_after_nshifts':'^[0-9]+$',
            'bad_weekend' :'^[0-1]$'
        }
        # unw_shifts, nw_days, nw_shifts_on_dates
        
        for key , val in keys.items():
            if not ( (key in data) and (re.match(val, data[key])) ):
                val_errors.append("in "+key)
                
        if len(val_errors) != 0:
            ret_message = "Validate error(s)"
            raise ValueError

        Employee.objects(id=id).update_one(set__max_assigns = int(data['max_assigns']))
        Employee.objects(id=id).update_one(set__min_assigns = int(data['min_assigns']))
        Employee.objects(id=id).update_one(set__max_cons_wdays = int(data['max_cons_wdays']))
        Employee.objects(id=id).update_one(set__min_cons_wdays = int(data['min_cons_wdays']))
        Employee.objects(id=id).update_one(set__max_cons_daysoff = int(data['max_cons_daysoff']))
        Employee.objects(id=id).update_one(set__min_cons_daysoff = int(data['min_cons_daysoff']))
        Employee.objects(id=id).update_one(set__max_cons_weekends = int(data['max_cons_weekends']))
        Employee.objects(id=id).update_one(set__daysoff_after_nshifts = int(data['daysoff_after_nshifts']))
        Employee.objects(id=id).update_one(set__bad_weekend = bool(data['bad_weekend']))
        
        # unw_shifts, nw_days, nw_shifts_on_dates
        # return 200 Success
        response.headers['Content-Type'] = 'application/json'
        response.status = 200
        return json.dumps({"message" : "Document updated"})

    except ValueError:
        response.status = 400
        if len(val_errors) != 0:
         return json.dumps({"message":ret_message , "erros":val_errors}) 
        
        return json.dumps({"message" : ret_message})

    except KeyError:
        response.status = 400
        return json.dumps({"message" : ret_message})
    
    except DoesNotExist:
        response.status = 404
        return json.dumps({"message" : ret_message})
    
    except ValidationError:
        response.status = 406
        return json.dumps({"message" : ret_message})

@get('/generate/:days')
def generate_schedule(days):
    
    return days