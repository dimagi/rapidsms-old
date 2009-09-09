import time
from datetime import datetime, timedelta
from reporters.models import Reporter, PersistantBackend
from rapidsms.tests.scripted import TestScript
from models import *
import reporters.app as reporters_app
import scheduler.app as scheduler_app
import weltel.app as weltel_app
import form.app as form_app
from weltel.formslogic import WeltelFormsLogic
from weltel.app import SAWA_CODE, SHIDA_CODE

class TestApp (TestScript):
    #apps = ([scheduler_app.App])
    apps = (reporters_app.App, form_app.App, scheduler_app.App, weltel_app.App )
    
    def setUp(self):
        TestScript.setUp(self)


    def test_patient_registration(self):
        script = """
            # new patient new number
            1234 > well register tst/1 female
            1234 < Patient tst/1 registered with new number 1234
            # new patient old number
            1236 > well register tst/2 f 1234
            1236 < Patient tst/2 registered with existing number 1234 (from patient tst/1)
            # old patient new number
            1234 > well register tst/1 male 1235
            1234 < Patient tst/1 reregistered with new number 1235
            # old patient old number belonging to patient
            1237 > well register tst/1 m 1235
            1237 < Patient tst/1 reregistered with existing number 1235
            # old patient old number not belonging to patient
            1234 > well register tst/1 FEMALE
            1234 < Patient tst/1 reregistered with existing number 1234 (from patient tst/2)
            1234 > well unsubscribe
            1234 < Kwaheri
            1234 > well subscribe
            1234 < Karibu
        """
        
    def test_patient_registration_err(self):
        script = """
            1238 > well register
            1238 < This number is not registered. To register, text: 'well register patient_id gender (phone_number)
            1238 > well register 1
            1238 < Error. Poorly formatted patient_id: 1
            1238 > well register f tst/1
            1238 < Error. Poorly formatted patient_id: f
        """

    def test_nurse_registration(self):
        script = """
            # new nurse
            1240 > well nurse tst
            1240 < Nurse 1240 registered with new number 1240
            # old
            1240 > well nurse tst
            1240 < Nurse 1240 reregistered with existing number 1240
            # new nurse old number
            1241 > well register tst/3 f
            1241 < Patient tst/3 registered with new number 1241
            1241 > well nurse tst
            1241 < Nurse 1241 registered with existing number 1241 reregistered from tst/3
            1241 > well unsubscribe
            1241 < Kwaheri
            1241 > well subscribe
            1241 < Karibu
        """
        
    def test_nurse_registration_err(self):
        script = """
            # new nurse
            1240 > well nurse
            1240 < This number is not registered. To register, text: 'well register patient_id gender (phone_number)
        """
        
    def test_commands(self):
        script = """
            1242 > well phone tst/4
            1242 < Phone number 1242 has been registered to patient tst/4
            1243 > well phone tst/4
            1243 < Phone number 1242 has been registered to patient tst/4
            1244 > well phone tst/4
            1244 < Phone number 1242 has been registered to patient tst/4
            1244 > well phones
            1244 < 1242, 1243, 1244
            1244 > well set phone
            1244 < Patient tst/4 default phone set to 1244
            1244 > well set phone
            1244 < Patient tst/4 default phone is 1244
            1242 > well set phone
            1242 < Patient tst/4 default phone set to 1242
            1242 > well get phone
            1242 < Patient tst/4 default phone is 1242
        """
        
    def test_sawa_shida(self):
        script = """
            1245 > well register tst/5 female
            1245 < Phone number 1245 has been registered to patient tst/5
            1245 > sawa
            1245 < Asante
            1245 > shida
            1245 < Pole
            1245 > shida sick
            1245 < Pole for 'Sick'
            1245 > Unrecognized randomness
            1245 < Command not recognized
        """
        
    def test_outcome(self):
        script = """
            1246 > well nurse tst
            1246 < Nurse registered with new number 1246
            1247 > well register tst/6 female
            1247 < Phone number 1247 has been registered to patient tst/6
            1248 > well register tst/7 male
            1248 < Phone number 1248 has been registered to patient tst/7
            1246 > tst/6 1
            1246 < Patient tst/6 updated to 'No Answer'
            1246 > tst/7 2
            1246 < Patient tst/1 updated to 'Gone'
        """
    
    def test_mambo(self):
        wfl = WeltelFormsLogic()
        backend = PersistantBackend.objects.get_or_create(slug=self.backend.slug)[0]
        patient, response = wfl.get_or_create_patient("tst/8", \
                                                      phone_number="1250", \
                                                      backend=backend, 
                                                      gender="f", 
                                                      date_registered=datetime.now())
        schedule = EventSchedule(callback="weltel.callbacks.send_mambo", \
                                 minutes='*', callback_args=[patient.id] )
        schedule.save()
        # speedup the scheduler so that 1 second == 1 minute
        self.router.start()
        self.router.get_app('scheduler').schedule_thread._debug_speedup(minutes=1)
        time.sleep(3.0)
        script = """
            1250 < Mambo?
            1250 < Mambo?
            1250 < Mambo?
        """
        self.runScript(script)
        self.router.stop()
        schedule.delete()
        
    def test_automatic_deregistration(self):
        # create patient
        wfl = WeltelFormsLogic()
        backend = PersistantBackend.objects.get_or_create(slug=self.backend.slug)[0]
        delta = timedelta(weeks=3)
        registered = datetime.now() - delta
        patient, response = wfl.get_or_create_patient("tst/9", \
                                                      phone_number="1251", \
                                                      backend=backend, 
                                                      gender="m", 
                                                      date_registered=registered)
        # setup timeout after one week
        schedule = EventSchedule(callback="weltel.callbacks.automatic_deregistration", \
                                 days_of_week='*', hours='*', minutes='*', callback_args=[1] )
        schedule.save()
        self.router.start()
        # speedup the scheduler so that 1 second == 7 days
        self.router.get_app('scheduler').schedule_thread._debug_speedup(days=7)

        # test tst/9 is inactive
        time.sleep(3.0)
        updated_patient = Patient.objects.get(id=patient.id)
        self.assertTrue(updated_patient.active==False)

        # reactivate
        patient.register_event(SAWA_CODE)
        time.sleep(1.0)
        updated_patient = Patient.objects.get(id=patient.id)
        self.assertTrue(updated_patient.active==True)
        
        #wrap up
        self.router.stop()
        schedule.delete()
            
    def test_shida_report(self):
        wfl = WeltelFormsLogic()
        backend = PersistantBackend.objects.get_or_create(slug=self.backend.slug)[0]
        nurse, response = wfl.get_or_create_nurse(site_code="tst", \
                                                  phone_number="1252", \
                                                  backend=backend)
        # timeout after one week
        schedule = EventSchedule(callback="weltel.callbacks.shida_report", \
                                 minutes='*')
        schedule.save()
        # speedup the scheduler so that 1 second == 7 days
        self.router.start()
        self.router.get_app('scheduler').schedule_thread._debug_speedup(minutes=1)
        time.sleep(1.0)
        # test regular report
        script = """
            1252 < no problem patients
        """
        self.runScript(script)
        
        # wrap up
        self.router.stop()
        schedule.delete()
        
