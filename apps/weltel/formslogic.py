#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
from rapidsms.i18n import ugettext_noop as _
from form.formslogic import FormsLogic
from rapidsms.i18n import ugettext_noop as _
from reporters.models import PersistantConnection
from weltel.models import Site, Patient, Nurse, MALE, FEMALE

#TODO - add basic check for when people submit fields in wrong order
#TODO - wrap the validation and actions in pretty wrapper functions

class WeltelFormsLogic(FormsLogic):
    ''' This class will hold the Weltel-specific forms logic. '''
    
    register_command = _("Correct format: 'well register site_id patient_id gender (phone_number)")
    nurse_command = _("Correct format: 'well nurse site_id")
    
    def validate(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        data = form_entry.to_dict()

        if form_entry.form.code.abbreviation == "register":
            site_code = data["site_code"]
            if len(site_code) == 0:
                return [_("Missing 'site code'.") + self.register_command ]
            patient_id = data["patient_id"]
            if len(patient_id) == 0:
                return [_("Missing 'patient_id'.") + self.register_command ]
            gender = (data["gender"] if "gender" in data else None)
            phone_number = (data["phone_number"] if "phone_number" in data else None)
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
            # all fields were present and correct, so copy them into the
            # form_entry, for "actions" to pick up again without re-fetching
            form_entry.reg_data = data
            return False
        
        elif form_entry.form.code.abbreviation == "nurse":
            site_code = data["site_code"]
            if len(site_code) == 0:
                return [_("Missing 'site_code'.") + self.nurse_command ]
            try:
                Site.objects.get(code=site_code)
            except Site.DoesNotExist:
                return [_("Unknown sitecode %(code)s") % {"code" : site_code}]
            # TODO - check if nurse exists already.
            # or do we allow new registrations to override old ones?
            form_entry.nurse_data = data
            return False
        
        elif form_entry.form.code.abbreviation == "set": 
            return False
        elif form_entry.form.code.abbreviation == "phone": 
            patient_id = data["patient_id"]
            # TODO - add patient validation
            form_entry.phone_data = data
            return False

    def actions(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        # language = get_language_code(message.persistant_connection)
        
        if form_entry.form.code.abbreviation == "register": 
            patient_id = form_entry.reg_data["patient_id"]
            patient, p_created = Patient.objects.get_or_create(alias=patient_id)
            if p_created:
                message.respond(_("Patient %(id)s registered") % {"id": patient.patient_id })
            patient.site_code = form_entry.reg_data["site_code"]
            if len(form_entry.reg_data["phone_number"])>0:
                phone_number = form_entry.reg_data["phone_number"]
            else: phone_number = None
            #patient.registered=message.date
            if "gender" in form_entry.reg_data:
                if form_entry.reg_data["gender"].startswith('m'):
                    patient.gender = MALE
                elif form_entry.reg_data["gender"].startswith('f'):
                    patient.gender = FEMALE
            
            # save connections
            if not phone_number: phone_number = message.persistant_connection.identity
            conn, c_created = PersistantConnection.objects.get_or_create(identity= phone_number, \
                                                       backend= message.persistant_connection.backend)
            if conn.reporter is None:
                message.respond(_("Patient %(id)s registered with new number %(num)s") % \
                                {"id": patient.patient_id, "num": phone_number})
            else:
                message.respond(_("Number %(num)s reregistered to patient %(id)s from %(old_id)s") % \
                                {"id": patient.patient_id, "num": phone_number, "old_id": conn.reporter.alias })                    
            conn.reporter = patient
            conn.save()
            
            patient.default_connection = conn
            patient.save()
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
            pass

