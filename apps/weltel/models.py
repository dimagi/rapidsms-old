from datetime import datetime
from django.db import models
from reporters.models import Reporter, PersistantConnection, Location 
from locations.models import Location

class Site(Location):
    """ This model represents a WelTel site """
    # fields TBD
    pass

class WeltelUser(Reporter):
    """ This model represents any weltel users """
    subscribed = models.BooleanField(default=True)
    class Meta:
        abstract = True
        
    def unsubscribe(self):
        self.set_subscribe(False)

    def set_subscribe(self, bool):
        if self.subscribed != bool:
            self.subscribed = bool
            self.save()
            if not self.subscribed:
                # delete all scheduled alerts for this user
                schedules = EventSchedule.objects.filter(callback_args__contains=self.id).delete()

class Nurse(WeltelUser):
    """ This model represents a nurse for WelTel. 
    
    """  
    # Nurses can be associated with zero or more locations
    # this could get very confusing, since 'reporters' has its own 'location'
    # field. But that's a hack, so we shouldn't use it.
    sites = models.ManyToManyField(Site, null=True)

    def __unicode__(self):
        if self.alias: return self.alias
        return self.id
    
    def subscribe(self):
        super(Nurse, self).set_subscribe(True)
        # set up weekly mambo schedule for friday @ 12:30 pm
        set_weekly_event("weltel.callbacks.shida_report", day=5, hour=12, \
                         minute=30, callback_args=self.id)

MALE = 'm'
FEMALE = 'f'
GENDER_CHOICES=(
    (MALE, 'male'),
    (FEMALE,'female')
)

class Patient(WeltelUser):
    """ This model represents a patient for WelTel """
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    state = models.ForeignKey("PatientState")
    active = models.BooleanField(default=True)
    site = models.ForeignKey(Site)
    
    def __unicode__(self):
        if self.alias: return self.alias
        if self.connection: return self.connection.identity
        return self.id
        
    # make 'patient_id' an alias for reporter.alias
    def _get_patient_id(self):
        return self.alias
    def _set_patient_id(self, value):
        self.alias = value
    patient_id = property(_get_patient_id, _set_patient_id)
    
    def register_event(self, code, issuer=None):
        event = EventType.objects.get(code=code)
        self.state = event.next_state
        self.save()
        if issuer is None: issuer = self
        EventLog(event=event, patient=self, triggered_by=issuer).save()

    def subscribe(self):
        super(Nurse, self).set_subscribe(True)
        # set up weekly mambo schedule for friday @ 12:30 pm
        set_weekly_event("weltel.callbacks.send_mambo", day=5, hour=12, \
                         minute=30, callback_args=self.id)

class PatientState(models.Model):
    code = models.CharField(max_length=15)
    name = models.CharField(max_length=63, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return self.name if self.name else self.code
    
# events in a patient's history
# - can be associated with a state transition
class EventType(models.Model):
    code = models.CharField(max_length=15)
    name = models.CharField(max_length=63, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    next_state = models.ForeignKey(PatientState)

    def __unicode__(self):
        return self.name if self.name else self.code

    #automatic deregistration
    #unsubscribe

class ProblemType(EventType):
    """ Patient reports a problem """
    class Meta:
        abstract = True
            
class OutcomeType(EventType):
    """ Nurse reports an outcome """
    class Meta:
        abstract = True

class EventLog(models.Model):
    event = models.ForeignKey(EventType)
    date = models.DateTimeField(null=False, default=datetime.now() )
    patient = models.ForeignKey(Patient)
    # can be triggered by patient, nurse, admin, IT, etc.
    # through sms, webui, etc. 
    triggered_by = models.CharField(max_length=63, null=True)
    notes = models.CharField(max_length=255, null=True)
    active = models.BooleanField(default=True)
    subscribed = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name if self.name else self.code
