from __future__ import print_function
from ortools.sat.python import cp_model
from bottle import request, response
from bottle import post
import json
import re

from db import *
import scheduler

@post('/schedule')
def create_schedule():
    ret_message = ""
    ext_errors = []
    val_errors = []
    employees = []
    response.headers['Content-Type'] = 'application/json'    
    try:
        # request 
        try:
            data = request.json
            # print(data)
        except:
            ret_message = "Bad json format."
            raise ValueError
        if data is None: 
            ret_message = "Request is null."
            raise KeyError

        # extract json
        keys = {'employees' , 'weeks'}
        for key  in keys:
            if not key in data:
                ext_errors.append("{} was not found in json.".format(key))
        
        if len(ext_errors) != 0:
            ret_message = "Extract error(s)."
            raise ValueError

        # validate weeks
        if not re.match(r'^[-+]?[0-9]+$',data['weeks']):
            val_errors.append("'weeks' is not integer.")
        
        # validate employees
        if not isinstance(data['employees'], list):
            val_errors.append("'employees' is not list")
        
        for id in data['employees']:
            try:
                document = Employee.objects.get(id=id).to_json()
            except DoesNotExist:
                val_errors.append("No document found with '_id' = {}.".format(id))
            except ValidationError:
                val_errors.append("{} is not a valid '_id'".format(id))
        
        if len(val_errors) != 0:
            ret_message = "Validation error(s)."
            raise ValueError

        
        # TODO: overflow check

        
        
        # return 201 Success
        response.status = 201
        return solve_shift_scheduling(data['employees'],int(data['weeks']))
           
    except ValueError:
        response.status = 400
        if len(val_errors) != 0:
            return json.dumps({"message":ret_message , "erros":val_errors}) 
        elif len(ext_errors) != 0: 
            return json.dumps({"message":ret_message , "erros":ext_errors}) 
        
        return json.dumps({"message" : ret_message})

    except KeyError:
        response.status = 400
        return json.dumps({"message" : ret_message}) 
