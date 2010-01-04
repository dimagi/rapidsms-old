import time
from datetime import datetime, timedelta
from reporters.models import Reporter, PersistantBackend
from rapidsms.tests.scripted import TestScript
import reporters.app as reporters_app
import scheduler.app as scheduler_app
import form.app as form_app
import weltel.app as weltel_app
from weltel.models import *
from weltel.formslogic import WeltelFormsLogic
from weltel.app import SAWA_CODE, SHIDA_CODE

class TestSchedule (TestScript):
    #apps = ([scheduler_app.App])
    apps = (reporters_app.App, form_app.App, scheduler_app.App, weltel_app.App )
    
    def setUp(self):
        TestScript.setUp(self)
    
    def test_mambo(self):
        wfl = WeltelFormsLogic()
        backend = PersistantBackend.objects.get_or_create(slug=self.backend.slug)[0]
        patient, response = wfl.get_or_create_patient("BA108", \
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
        patient, response = wfl.get_or_create_patient("BA109", \
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

        # test BA109 is inactive
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
            
    def test_shida_report_basic(self):
        """ it's difficult to check shida_empty and shida in sequence
        since self.runScript stops the router (without any sleep's)
        and we rely on activities in different threads)
        """
        wfl = WeltelFormsLogic()
        backend = PersistantBackend.objects.get_or_create(slug=self.backend.slug)[0]
        nurse, response = wfl.get_or_create_nurse(site_code="BA1", \
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
            1252 < No problem patients
        """
        self.runScript(script)
        
        # wrap up
        self.router.stop()
        schedule.delete()
        
    def test_shida_report(self):
        wfl = WeltelFormsLogic()
        backend = PersistantBackend.objects.get_or_create(slug=self.backend.slug)[0]
        nurse, response = wfl.get_or_create_nurse(site_code="BA1", \
                                                  phone_number="1252", \
                                                  backend=backend)
        # timeout after one week
        schedule = EventSchedule(callback="weltel.callbacks.shida_report", \
                                 minutes='*')
        schedule.save()
        # create problem patients
        patient, response = wfl.get_or_create_patient("BA1010", \
                                                      phone_number="1257", \
                                                      backend=backend, 
                                                      gender="m",
                                                      date_registered=datetime.now())
        patient.register_event(SHIDA_CODE)
        # create problem patients
        patient2, response = wfl.get_or_create_patient("BA1011", \
                                                      phone_number="1258", \
                                                      backend=backend, 
                                                      gender="m",
                                                      date_registered=datetime.now())
        patient2.register_event(SHIDA_CODE)
        # speedup the scheduler so that 1 second == 7 days
        self.router.start()
        self.router.get_app('scheduler').schedule_thread._debug_speedup(minutes=1)
        time.sleep(1.0)
        # test regular report
        script = """
            1252 < BA1010 1257 shida BA1011 1258 shida
        """
        self.runScript(script)
        schedule.delete()

