import logging
from rapidsms.message import Message
from reporters.models import Reporter
from logger.models import IncomingMessage
from weltel.models import Site, Nurse, Patient, PatientState

######################
# Callback Functions #
######################

def send_mambo(router, reporter_id):
    connection = Reporter.objects.get(reporter_id).connection()
    response = "Mambo?"
    logging.info("Sending: %s" % response)
    router.outgoing(Message(connection, response))

def automatic_deregistration(router, reporter_id):
    timeout_interval = timedelta(weeks=2)
    timeout = datetime.now() - timeout_interval
    # check if patients have not been seen in a while
    patients = Patient.objects.filter(location=site)
    active = patients.filter(active=True).filter(subscribed=True)
    for patient in active:
        active = False
        # check a) no messages in X time from any of their connections
        for conn in reporters.connections.all():
            log = IncomingMessage.objects.filter(identity= conn.identity, \
                                           backend= conn.backend)
            if log.received > timeout:
                active = True
                continue
        # check b) no status updates from nurse
        log_count = PatientStateLog.objects.filter(patient=patient).order_by("-date").count()
        if log_count>0:
            last_touched = PatientStateLog.objects.filter(patient=patient).order_by("-date")[0].date
            if last_touched > timeout:
                active = True
        if active == False:
            patient.active = False
            patient.save()
    return

def shida_report(router, reporter_id):
    # compile report for each site
    for site in Site.objects.all():
        # get all patients who responded shida, 'other', or are in the default state
        patients = Patient.objects.filter(location=site).filter(state__code__ne='sawa')
        # get all patients in sawa state but from whom we haven't heard in 3 weeks
        patients = patients + Patient.objects.filter(location=site).filter(state__code__eq='sawa', active=False)
        report = ''
        for patient in patients:
            report = report + "%s %s %s " % (patient.patient_id, \
                     patient.connection.identity, patient.state.code)
        # send report to all nurses registered for that site
        for nurse in Nurses.objects.filter(locations=site):
            connection = nurse.connection()
            if report:
                router.outgoing(Message(connection, report))
            else:
                router.outgoing(Message(connection, _("no problem patients")))
