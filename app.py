import sys
import bottle
from bottle import  get, put, delete

sys.path.insert(0, './endpoints')
sys.path.insert(0, './controllers')

import create_employee  
import delete_employee  
import read_all_employees  
import read_employee  
import update_employee_contract
import create_schedule


app = application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(host = '0.0.0.0',reloader=True ,port = 8000)
