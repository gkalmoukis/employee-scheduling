from mongoengine import *
import datetime

connect('db1')



class Employee(Document):
   'Common base class for all employees'
   name = StringField(required=True)
   email = EmailField(domain_whitelist=None, allow_utf8_user=False, allow_ip_domain=False, required=True )
   password = StringField(required=True)
   role = StringField(required=True)
   max_assigns = IntField(required=False)
   min_assigns = IntField(required=False)  
   max_cons_wdays = IntField(required=False)
   min_cons_wdays = IntField(required=False)
   max_cons_daysoff = IntField(required=False)
   min_cons_daysoff = IntField(required=False)
   max_cons_weekends = IntField(required=False)
   daysoff_after_nshifts = IntField(required=False)
   bad_weekend = BooleanField(required=False)