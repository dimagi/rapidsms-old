from django.db import models
from reporters.models import Reporter, PersistantConnection, Location 
from locations.models import Location

class Site(Location):
    """ This model represents a WelTel site """
    # fields TBD
    pass

class Nurse(Reporter):
    """ This model represents a nurse for WelTel. 
    
    """  
    # Nurses can be associated with zero or more locations
    # this could get very confusing, since 'reporters' has its own 'location'
    # field. But that's a hack, so we shouldn't use it.
    locations = models.ManyToManyField(Site, null=True)
    
MALE = 'm'
FEMALE = 'f'
GENDER_CHOICES=(
    (MALE, 'male'),
    (FEMALE,'female')
)

class Patient(Reporter):
    """ This model represents a patient for WelTel """
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    locations = models.ForeignKey(Site, null=True)
    default_connection = models.ForeignKey(PersistantConnection, null=True)
    
    # make 'patient_id' an alias for reporter.alias
    def _get_patient_id(self):
        return self.alias
    def _set_patient_id(self, value):
        self.alias = value
    patient_id = property(_get_patient_id, _set_patient_id)
