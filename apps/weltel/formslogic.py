#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
from rapidsms.i18n import ugettext_noop as _
from form.formslogic import FormsLogic
from reporters.models import PersistantConnection
from scheduler.models import set_weekly_event
from weltel.models import Site, Patient, PatientState, Nurse, MALE, FEMALE

REGISTER_COMMAND = _("Correct format: 'well register site_id patient_id gender (phone_number)")
NURSE_COMMAND = _("Correct format: 'well nurse site_id")

#TODO - add basic check for when people submit fields in wrong order
#TODO - wrap the validation and actions in pretty wrapper functions

class WeltelFormsLogic(FormsLogic):
    ''' This class will hold the Weltel-specific forms logic. '''    
    
    def validate(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        data = form_entry.to_dict()

        if form_entry.form.code.abbreviation == "register":
            ret = self.is_patient_invalid(data["site_code"], data["patient_id"], \
                                          data["gender"], data["phone_number"])
            if not ret: 
                # all fields were present and correct, so copy them into the
                # form_entry, for "actions" to pick up again without re-fetching
                form_entry.reg_data = data
            return ret
        elif form_entry.form.code.abbreviation == "nurse":
            ret = self.is_nurse_invalid(data["site_code"])
            if not ret: 
                # all fields were present and correct, so copy them into the
                # form_entry, for "actions" to pick up again without re-fetching
                form_entry.nurse_data = data
            return ret
        elif form_entry.form.code.abbreviation == "set": 
            return False
        elif form_entry.form.code.abbreviation == "phone": 
            patient_id = data["patient_id"]
            try:
                Patient.objects.get(alias=patient_id)
            except Patient.DoesNotExist:
                return [_("Unknown patient %(id)s.") % patient_id ]
            form_entry.phone_data = data
            return False

    def actions(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        # language = get_language_code(message.persistant_connection)
        
        if form_entry.form.code.abbreviation == "register":
            if len(form_entry.reg_data["phone_number"])>0:
                phone_number = form_entry.reg_data["phone_number"]
            else: 
                phone_number = message.persistant_connection.identity
            gender = None
            if "gender" in form_entry.reg_data:
                if form_entry.reg_data["gender"].startswith('m'):
                    gender = MALE
                elif form_entry.reg_data["gender"].startswith('f'):
                    gender = FEMALE
            #registered=message.date
            response = self.get_or_create_patient(form_entry.reg_data["site_code"], \
                                       form_entry.reg_data["patient_id"], \
                                       phone_number=phone_number, \
                                       backend= message.persistant_connection.backend, 
                                       gender=gender)
            message.respond(response)
        elif form_entry.form.code.abbreviation == "nurse":
            site_code =  form_entry.nurse_data["site_code"]
            try:
                site = Site.objects.get(code=site_code)
            except Site.DoesNotExist:
                message.respond(_("Site %(code)s does not exist") % {"code": site_code })
                return
            phone_number = message.persistant_connection.identity
            # for now, set unique id to be phone number
            nurse, n_created = Nurse.objects.get_or_create(alias= phone_number)
            nurse.locations.add(site)
            if n_created:
                message.respond(_("Nurse %(id)s registered") % {"id": nurse.alias })
            
            # save connections
            conn, c_created = PersistantConnection.objects.get_or_create(identity= phone_number, \
                                                       backend= message.persistant_connection.backend)
            if conn.reporter is None:
                message.respond(_("Nurse %(id)s registered with new number %(num)s") % \
                                {"id": nurse.alias, "num": phone_number})
            else:
                message.respond(_("Number %(num)s reregistered to nurse %(id)s from %(old_id)s") % \
                                {"id": nurse.alias, "num": phone_number, "old_id": conn.reporter.alias })                    
            conn.reporter = nurse
            conn.save()
        elif form_entry.form.code.abbreviation == "set":
            # see who this phone is registered to
            # set as their default
            try:
                patient = Patient.objects.get(id=message.persistant_connection.reporter.pk)
            except Patient.DoesNotExist:
                message.respond( "Phone number %(num)s is not registered" % \
                                 {"num": message.persistant_connection.identity } )
                return
            patient.default_connection = message.persistant_connection
            patient.save()
            message.respond( "Patient %(id)s default phone set to %(num)s" % \
                             {"num": message.persistant_connection.identity, "id":patient.patient_id } )
        elif form_entry.form.code.abbreviation == "phone":
            patient_id = form_entry.phone_data["patient_id"]
            patient = Patient.objects.get(alias = patient_id)

            conn, c_created = PersistantConnection.objects.get_or_create(identity=message.persistant_connection.identity, \
                                                       backend=message.persistant_connection.backend)
            if c_created:
                patient.connections.add(conn)
                message.respond( "Patient %(id)s registered phone %(num)s" % \
                                 {"id":patient.patient_id, "num":conn.identity} )
            else:
                message.respond( "Phone %(num)s already registered with Patient %(id)s" % \
                                 {"id":patient.patient_id, "num":conn.identity} )

    def is_patient_invalid(self, site_code, patient_id, gender=None, phone_number=None):
        if len(site_code) == 0:
            return [_("Missing 'site code'.") + REGISTER_COMMAND ]
        if len(patient_id) == 0:
            return [_("Missing 'patient_id'.") + REGISTER_COMMAND ]
        try:
            Site.objects.get(code=site_code)
        except Site.DoesNotExist:
            return [_("Unknown sitecode %(code)s") % {"code" : site_code}]
        if len(gender) > 0:
            if not gender.startswith('m') and not gender.startswith('f'):
                return [_("Invalid gender %(gender)s") % {"gender" : gender}]
        if len(phone_number) > 0:
            if not re.match(r"^\+?\d+$", phone_number):
                return [_("Invalid phone number %(num)s") % {"num" : phone_number}]
        return False
    
    def is_nurse_invalid(self, site_code):
        if len(site_code) == 0:
            return [_("Missing 'site_code'.") + NURSE_COMMAND ]
        try:
            Site.objects.get(code=site_code)
        except Site.DoesNotExist:
            return [_("Unknown sitecode %(code)s") % {"code" : site_code}]
        return False

    def get_or_create_patient(self, site_code, patient_id, phone_number=None, \
                              backend=None, gender=None, date_registered=None):
        response = ''
        try:
            patient = Patient.objects.get(alias=patient_id)
            p_created = False
        except Patient.DoesNotExist:
            patient = Patient(alias=patient_id)
            response = _("Patient %(id)s registered. ") % {"id": patient_id }
            p_created = True
        patient.site_code = site_code
        if gender: patient.gender = gender
        patient.state = PatientState.objects.get(code='default')
        patient.save()

        if phone_number is None:
            return response
        # save connections
        conn, c_created = PersistantConnection.objects.get_or_create(\
                          identity= phone_number, backend=backend)
        if conn.reporter is None:
            response = response + \
                       _("Patient %(id)s registered with new number %(num)s") % \
                       {"id": patient.patient_id, "num": phone_number}
        else:
            response = response + \
                       _("Number %(num)s reregistered to patient %(id)s from %(old_id)s") % \
                       {"id": patient.patient_id, "num": phone_number, "old_id": conn.reporter.alias }
        conn.reporter = patient
        conn.save()
        patient.default_connection = conn
        patient.save()
        
        if p_created:
            # set up weekly mambo schedule for friday @ 12:30 pm
            set_weekly_event("weltel.callbacks.send_mambo", day=5, hour=12, \
                             minute=30, callback_args=patient.id)
        return response
