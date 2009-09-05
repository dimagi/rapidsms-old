"""

WELTEL core logic

"""

import re
import rapidsms
import logging
from rapidsms.parsers.keyworder import Keyworder
from rapidsms.i18n import ugettext_noop as _
from reporters.models import Reporter
from weltel.formslogic import WeltelFormsLogic, REGISTER_COMMAND, NURSE_COMMAND
from weltel.models import Nurse, Patient, PatientState, OutcomeType, ProblemType, EventType

SAWA = 'sawa'
SHIDA = 'shida'
OTHER = 'other'

class App (rapidsms.app.App):
    kw = Keyworder()
    bootstrapped = False
    
    def start (self):
        """Configure your app in the start phase."""
        if not self.bootstrapped:
            # initialize the forms app for registration
            self._form_app = self.router.get_app("form")
            # this tells the form app to add itself as a message handler
            # which registers the regex and function that this will dispatch to
            self._form_app.add_message_handler_to(self)
            
            formslogic = WeltelFormsLogic()
            formslogic.app = self
            # this tells the form app that this is also a form handler 
            self._form_app.add_form_handler("weltel", formslogic)
            
            self.boostrapped = True
        
    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass

    def handle (self, message):
        try:
            message.patient = Patient.objects.get(reporter_ptr=message.reporter)
        except Patient.DoesNotExist:
            pass
        try:
            message.nurse = Nurse.objects.get(reporter_ptr=message.reporter)
        except Nurse.DoesNotExist:
            pass
        # use the keyworder to see if the forms app can help us
        try:
            if hasattr(self, "kw"):
                self.debug("WELTEL HANDLE")
                
                # attempt to match tokens in this message
                # using the keyworder parser
                results = self.kw.match(self, message.text)
                if results:
                    func, captures = results
                    # if a function was returned, then a this message
                    # matches the handler _func_. call it, and short-
                    # circuit further handler calls
                    func(self, message, *captures)
                    return True
                else:
                    self.other(message)
            else:
                self.debug("App does not instantiate Keyworder as 'kw'")
        except Exception:
            self.log_last_exception()
        
        # this is okay.  one of the other apps may yet pick it up
        self.info("Message doesn't match weltel. %s", message)    

    def cleanup (self, message):
        """Perform any clean up after all handlers have run in the
           cleanup phase."""
        pass

    def outgoing (self, message):
        """Handle outgoing message notifications."""
        pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass
    
    def add_message_handler(self, regex, function):
        '''Registers a message handler with this app.  
           Incoming messages that match this will call the function'''
        self.info("Registering regex: %s for function %s, %s" % \
                  (regex, function.im_class, function.im_func.func_name))
        self.kw.regexen.append((re.compile(regex, re.IGNORECASE), function))
 

    def is_patient(f):
        def new_f(self, message, *args):
            if not hasattr(message,'patient'):
                message.respond( _("This number is not registered.") + REGISTER_COMMAND )
                return
            f(self, message, *args)
        return new_f
        
    def is_nurse(f):
        def new_f(self, message, *args):
            if not hasattr(message,'patient'):
                message.respond( _("This number is not registered to a nurse.") )
                return
            f(self, message, *args)
        return new_f
        
    @kw("(sawa|poa|nzuri|safi)(.*)")
    @is_patient
    def sawa(self, message, sawa, extra=None):
        message.patient.register_event(SAWA)
        # Note that all messages are already logged in logger
        logging.info("Patient %s set to '%s'" % (message.patient.alias, SAWA))
        message.respond( _("Asante") )
    
    @kw("(shida)\s*([0-9])(.*)")
    @is_patient
    def shida(self, message, shida, problem_code, extra=None):
        response = ''
        try:
            message.patient.register_event(problem_code)
        except ProblemType.DoesNotExist:
            response = _("Problem %(code)s not recognized. ") % \
                        {'code':problem_code} 
            message.patient.register_event(SHIDA)
        logging.info("Patient %s set to '%s'" % (message.patient.alias, SHIDA) )
        message.respond( response + _("Pole %(code)s") % {'code':problem_code} )
    
    @kw("(shida)(whatever)?")
    @is_patient
    def shida_new(self, message, shida, new_problem=None):
        message.patient.register_event(SHIDA)
        logging.info("Patient %s set to '%s'" % (message.patient.alias, SHIDA) )
        message.respond( _("Pole") )
    
    @kw("(numbers)\s+(numbers)")
    @is_nurse
    def outcome(self, message, patient_id, outcome_code):
        """ Expecting a text from a nurse of the form: <patient-id> <outcome-code> """
        try:
            patient = Patient.objects.get(alias=patient_id)
        except Patient.DoesNotExist:
            message.respond( _("Patient (%(id)s) not recognized.")%{'id':patient_id} )
            return
        try:
            patient.register_event(outcome_code)
        except OutcomeType.DoesNotExist:
            message.respond( _("Outcome (%(code)s) not recognized.")%{'code':outcome_code} )
            return
        logging.info("Patient %s set to '%s'" % (message.patient.alias, outcome_code))
        message.respond( _("Patient %(id)s updated to %(code)s") % \
                         {'id':patient_id, 'code':outcome_code} )
        
    @is_patient
    def other(self, message):
        message.patient.register_event(OTHER)
        logging.info("Patient %s sent unrecognized command '%s'" % \
                     (message.patient.alias, OTHER))
        message.respond( _("Command not recognized.") )

