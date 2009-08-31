import time
from rapidsms.tests.scripted import TestScript
import scheduler.app as scheduler_app
from scheduler.models import EventSchedule

class TestApp (TestScript):
    apps = ([scheduler_app.App])
    
    def setUp(self):
        TestScript.setUp(self)
        EventSchedule.objects.all().delete()

    def test_one_shot(self):
        global callback_counter
        callback_counter=0
        self.router.start()
        self.router.get_app('scheduler').schedule_thread._debug_speedup(1)
        schedule = EventSchedule(callback="scheduler.tests.test_callback", 
                                 minutes='*', callback_args=([3]), count=3)
        schedule.save()
        time.sleep(4.0)
        self.assertEquals(callback_counter,9)
        self.router.stop()
        
def test_callback(arg):
    global callback_counter
    print "adding %s to global_var (%s)" % (arg, callback_counter)
    callback_counter = callback_counter + arg
