from bottle import request, response
from bottle import put
import json
import re
from db import *

@put('/employee_contract/:id')
def update_employee_contract(id):
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