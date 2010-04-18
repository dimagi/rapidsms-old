'''
Created on Mar 31, 2010

@author: Drew Roos
'''

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rapidsms.webui.utils import paginated, render_to_response
from circumcision.models import *
import circumcision.config as config
from datetime import date

def patient_list (request):
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
            {'days': config.notification_days, 'patients': paginated(request, regs)})
    
def patient_update (request, patid):
    patient = get_object_or_404(Registration, patient_id=patid)
    
    