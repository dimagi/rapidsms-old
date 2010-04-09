'''
Created on Mar 31, 2010

@author: Drew Roos
'''

from django.db import models
from reporters.models import PersistantConnection

class Registration(models.Model):
    patient_id = models.CharField(max_length=20, primary_key=True)
    contact_time = models.IntegerField()
    connection = models.ForeignKey(PersistantConnection, unique=True)
    registered_on = models.DateField(auto_now_add=True)
    language = models.CharField(max_length=20)
    
    def __unicode__ (self):
        return 'registration: %s %d %s %s %s' % (self.patient_id, self.contact_time,
            str(self.connection), str(self.registered_on), self.language)