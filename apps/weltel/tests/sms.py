import time
from datetime import datetime, timedelta
from reporters.models import Reporter, PersistantBackend
from rapidsms.tests.scripted import TestScript
from weltel.models import *
import logger.app as logger_app
import reporters.app as reporters_app
import scheduler.app as scheduler_app
import weltel.app as weltel_app
import form.app as form_app
from weltel.formslogic import WeltelFormsLogic
from weltel.app import SAWA_CODE, SHIDA_CODE

class TestSMS (TestScript):
    apps = (logger_app.App, reporters_app.App, form_app.App, scheduler_app.App, weltel_app.App )
    
    def setUp(self):
        TestScript.setUp(self)
        
    testOutcomeToOtherPhone = """
        1248 > well register BA107 male
        1248 < Patient BA107 registered with new number 1248
        1299 > BA107 2
        1299 < Command not recognized
    """

    test_unknown_patient_other = """
        # (%s)\s*(.*)" % PATIENT_ID_REGEX)
        1240 > XY10001 1
        1240 < Unknown patient XY10001.
        """
    
    test_unknown_site_patient = """
        # new patient - these have only been tested with empty db (no forms). may break once populated.
        1240 > well register nonexistantsite/1 female
        1240 < Error. Unknown sitecode non
        """
    
    test_unknown_site_nurse = """
        # new nurse - these have only been tested with empty db (no forms). may break once populated.
        1240 > well nurse nonexistantsite
        1240 < Error. Unknown sitecode nonexistantsite
        """
    
    test_unregistered = """
        1233 > asdf
        1233 < This number is not registered. To register, text: 'well register patient_id gender (phone_number)
    """

    test_patient_registration = """
        # new patient new number
        1234 > well register BA101 female
        1234 < Patient BA101 registered with new number 1234
        # new patient old number
        1236 > well register BA102 f 1234
        1236 < Patient BA102 registered with existing number 1234 (from patient BA101)
        # old patient new number
        1234 > well register BA101 male 1235
        1234 < Patient BA101 reregistered with new number 1235
        # old patient old number belonging to patient
        1237 > well register BA101 m 1235
        1237 < Patient BA101 reregistered with existing number 1235
        # old patient old number not belonging to patient
        1234 > well register BA101 FEMALE
        1234 < Patient BA101 reregistered with existing number 1234 (from patient BA102)
        1234 > well unsubscribe
        1234 < Kwaheri
        1234 > well subscribe
        1234 < Karibu
        """
        
    test_patient_registration_err = """
        1238 > well register
        1238 < This number is not registered. To register, text: 'well register patient_id gender (phone_number)
        1238 > well register 1
        1238 < Error. Poorly formatted patient_id: 1
        1238 > well register f BA101
        1238 < Error. Poorly formatted patient_id: f
        """

    test_nurse_registration = """
        # new nurse
        1240 > well nurse BA1
        1240 < Nurse registered with new number 1240
        # old
        1240 > well nurse BA1
        1240 < Nurse reregistered with existing number 1240
        # new nurse old number
        1241 > well register BA103 f
        1241 < Patient BA103 registered with new number 1241
        1241 > well nurse BA1
        1241 < Nurse registered with existing number 1241 reregistered from BA103
        1241 > well unsubscribe
        1241 < Kwaheri
        1241 > well subscribe
        1241 < Karibu
        """
        
    test_nurse_registration_err = """
        # new nurse
        1240 > well nurse
        1240 < This number is not registered. To register, text: 'well register patient_id gender (phone_number)
        """
        
    test_commands = """
        1242 > well register BA104 m
        1242 < Patient BA104 registered with new number 1242
        1243 > well phone BA104
        1243 < Phone number 1243 has been registered to patient BA104
        1244 > well phone BA104
        1244 < Phone number 1244 has been registered to patient BA104
        1244 > well phones
        1244 < 1242, 1243, 1244
        1244 > well set phone
        1244 < Patient BA104 default phone set to 1244
        1244 > well get phone
        1244 < Patient BA104 default phone is 1244
        1242 > well set phone
        1242 < Patient BA104 default phone set to 1242
        1242 > well get phone
        1242 < Patient BA104 default phone is 1242
        """
        
    testSawaShida = """
        1245 > well register BA105 female
        1245 < Patient BA105 registered with new number 1245
        1245 > sawa
        1245 < Asante
        1245 > shida
        1245 < Pole
        1245 > shida 1
        1245 < Pole for 'No Answer'
        1245 > Unrecognized randomness
        1245 < Command not recognized
        """
        
    testOutcome = """
        1246 > well nurse BA1
        1246 < Nurse registered with new number 1246
        1247 > well register BA106 female
        1247 < Patient BA106 registered with new number 1247
        1248 > well register BA107 male
        1248 < Patient BA107 registered with new number 1248
        1246 > BA106 1
        1246 < Patient BA106 updated to 'No Answer'
        1246 > BA107 2
        1246 < Patient BA107 updated to 'Disappeared'
        """
    
    testShidaReport = """
        1260 > well register BA1011 female
        1260 < Patient BA1011 registered with new number 1260
        1261 > well register BA1012 female
        1261 < Patient BA1012 registered with new number 1261
        1262 > well nurse BA1
        1262 < Nurse registered with new number 1262
        1262 > well report
        1262 < BA1011 1260 default BA1012 1261 default
        1260 > sawa
        1260 < Asante
        1262 > well report
        1262 < BA1012 1261 default
        1261 > sawa
        1261 < Asante
        1262 > well report
        1262 < No problem patients
        1260 > shida
        1260 < Pole
        1262 > well report
        1262 < BA1011 1260 shida
        1261 > shida 2
        1261 < Pole for 'Disappeared'
        1262 > well report
        1262 < BA1011 1260 shida BA1012 1261 other
        1261 > sawa
        1261 < Asante
        1262 > well report
        1262 < BA1011 1260 shida
        """
        
        # We should also test what happens to the shida report
        # after 'unsubscribe' and 'inactive' 
        # (once we get clarification from ana)

        
