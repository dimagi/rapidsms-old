from datetime import datetime
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

class PatientState(models.Model):
    code = models.CharField(max_length=15)
    name = models.CharField(max_length=63, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return self.name if self.name else self.code

class Patient(Reporter):
    """ This model represents a patient for WelTel """
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    locations = models.ForeignKey(Site, null=True)
    default_connection = models.ForeignKey(PersistantConnection, null=True)
    state = models.ForeignKey(PatientState, default=PatientState.objects.get(code='default') )
    
    # make 'patient_id' an alias for reporter.alias
    def _get_patient_id(self):
        return self.alias
    def _set_patient_id(self, value):
        self.alias = value
    patient_id = property(_get_patient_id, _set_patient_id)

# an event log showing when patients states were manually transitioned
# (i.e. when a nurse submitted a follow up report that resulted in a
# state transition)
class PatientStateLog(models.Model):
    patient = models.ForeignKey(Patient)
    transitioned_to = models.ForeignKey(PatientState, null=True)
    # typically, nurses will trigger transitions
    # but one can imagine an administrator doing it via a webui or something
    by = models.CharField(max_length=63, null=True)
    date = models.DateTimeField(null=False, default=datetime.now() )
    def __unicode__(self):
        return self.name if self.name else self.code
    # TODO - link this to patient.save()

