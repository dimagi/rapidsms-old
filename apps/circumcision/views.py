'''
Created on Mar 31, 2010

@author: Drew Roos
'''

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rapidsms.webui.utils import paginated, render_to_response
from circumcision.models import *
from circumcision.app import split_contact_time
import circumcision.config as config
from datetime import date
from django.forms import ModelForm, HiddenInput

def patient_list (request):

    #handle submission for updating a patient (from /patient/xxx/)
    patient_id = None
    if request.method == 'POST' and 'patient_id' in request.POST:
        patient_id = request.POST['patient_id']
    save_msg = None
    if patient_id != None:
        form = PatientForm(request.POST, instance=Registration.objects.get(patient_id=patient_id))
        if form.is_valid():
            form.save()
            save_msg = 'Successfully updated patient %s' % patient_id
        else:
            save_msg = 'Unable to update patient %s! %s' % (patient_id, form.errors)
    
    regs = Registration.objects.all().order_by('-registered_on')
    sentlog = SentNotif.objects.all()
    
    sent = {}
    for s in sentlog:
        patid = s.patient_id
        day = s.day
        
        if patid not in sent:
            sent[patid] = set()
        days = sent[patid]
        days.add(day)
    
    for r in regs:
        days = sent[r.patient_id] if r.patient_id in sent else set()
        dayslist = []
        for i in config.notification_days:
            dayslist.append(i in days)
        
        r.notifications = dayslist
        r.post_op = (date.today() - r.registered_on).days
    
    return render_to_response(request, 'circumcision/overview.html',
            {'days': config.notification_days, 'patients': paginated(request, regs), 'save_msg': save_msg})
    
def patient_update (request, patid):
    patient = get_object_or_404(Registration, patient_id=patid)
    form = PatientForm(instance=patient)
    
    sent = SentNotif.objects.filter(patient_id=patient)
    patient.notifications = ', '.join(sorted([s.day for s in sent])) if len(sent) > 0 else 'none sent yet'
    patient.post_op = (date.today() - patient.registered_on).days
    patient.contact_time = '%02d:%02d' % split_contact_time(patient.contact_time)
    
    return render_to_response(request, 'circumcision/patient.html',
            {'px': patient, 'pat_form': form})
    
class PatientForm(ModelForm):
    class Meta:
        model = Registration
        fields = ['patient_id', 'followup_visit', 'final_visit']
        
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['patient_id'].widget = HiddenInput()