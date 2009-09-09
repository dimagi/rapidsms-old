import logging
from datetime import datetime, timedelta
from rapidsms.message import Message
from rapidsms.i18n import ugettext_noop as _
from logger.models import IncomingMessage
from weltel.models import Site, Nurse, Patient, PatientState, EventLog

######################
# Callback Functions #
######################

def send_mambo(router, patient_id):
    response = "Mambo?"
    logging.info("Sending: %s" % response)
    connection = Patient.objects.get(id=patient_id).connection
    be = router.get_backend(connection.backend.slug)
    be.message(connection.identity, response).send()

def automatic_deregistration(router, timeout_weeks):
    timeout_interval = timedelta(weeks=timeout_weeks)
    timeout = datetime.now() - timeout_interval
    # check if patients have not been seen in a while
    patients = Patient.objects.all()
    active = patients.filter(active=True).filter(subscribed=True)
    for patient in active:
        active = False
        # check a) no messages in X time from any of their connections
        for conn in patient.connections.all():
            try:
                log = IncomingMessage.objects.latest()
            except IncomingMessage.DoesNotExist:
                if patient.date_registered > timeout:
                    active = True
                # no messages received yet. TODO: check for the signup date of the patient.
                # once we start logging sign-up dates, that is. 
            else:
                if log.received > timeout:
                    active = True
                    continue
        # check b) no status updates from nurse
        try:
            last_touched = EventLog.objects.filter(patient=patient).latest()
        except EventLog.DoesNotExist:
            pass
        else:
            if last_touched.date > timeout:
                active = True
        if active == False:
            patient.active = False
            patient.save()
    return

def shida_report(router):
    # compile report for each site
    for site in Site.objects.all():
        sawa = PatientState.objects.get(code='sawa')
        patient_set = set()
        # get all patients who responded shida, 'other', or are in the default state
        patients = Patient.objects.filter(location=site).exclude(state=sawa)
        for patient in patients:
            patient_set.add(patient)
        # get all patients in sawa state but from whom we haven't heard in 3 weeks
        patients = Patient.objects.filter(location=site).filter(state=sawa, active=False)
        for patient in patients:
            patient_set.add(patient)
        
        # generate report
        report = ''
        for patient in patient_set:
            report = report + "%s %s %s " % (patient.patient_id, \
                     patient.connection.identity, patient.state.code)
        # send report to all nurses registered for that site
        for nurse in Nurse.objects.filter(sites=site):
            be = router.get_backend(nurse.connection.backend.slug)
            if report:
                be.message(nurse.connection.identity, report).send()
            else:
                be.message(nurse.connection.identity, _("no problem patients")).send()

