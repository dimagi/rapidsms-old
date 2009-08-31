#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import time
import threading
from datetime import datetime, timedelta

import rapidsms

from scheduler.models import EventSchedule

class App (rapidsms.app.App):
    """ This app provides cron-like functionality for scheduled tasks,
    as defined in the django model EventSchedule
    
    """
    
    bootstrapped = False

    def start (self):
        if not self.bootstrapped:
            # interval to check for scheduled events (in seconds)
            schedule_interval = 60
            # launch scheduling_thread
            self.schedule_thread = SchedulerThread(schedule_interval)
            self.schedule_thread.start()
            self.bootstrapped = True

    def stop (self):
        self.schedule_thread.stop()

class SchedulerThread (threading.Thread):
    _speedup = 0
    
    def __init__ (self, schedule_interval):
        super(SchedulerThread, self).__init__(\
            target=self.scheduler_loop,\
            args=(schedule_interval,))
        self.daemon = True
        self._stop = threading.Event()
        self._speedup = 0

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def _debug_speedup(self, speedup):
        """ This function is purely for the sake of debugging/unit-tests 
        It specifies a time interval in minutes by which the scheduler
        loop jumps ahead. This makes it possible to test long-term intervals
        quickly.
        
        Arguments: speedup - speedup interval in minutes
        """
        self._speedup = speedup
            
    def scheduler_loop(self, interval=60):
        now = datetime.now()
        while not self.stopped():
            event_schedules = EventSchedule.objects.all()
            for schedule in event_schedules:
                if schedule.should_fire(now):
                    # call the callback function
                    # possibly passing in args and kwargs
                    module, callback = schedule.callback.rsplit(".", 1)
                    module = __import__(module, globals(), locals(), [callback])
                    callback = getattr(module, callback)
                    callback(*schedule.callback_args, **schedule.callback_kwargs)

                    if schedule.count:
                        schedule.count = schedule.count - 1
                        # should we delete expired schedules? we do now.
                        if schedule.count <= 0: schedule.delete()
                        else: schedule.save()
                    # should we delete expired schedules? we do now.
                    if schedule.end_time:
                        if schedule.end_time > now:
                            schedule.delete()
            next_run = now + timedelta(seconds=interval)
            if self._speedup != 0: # debugging/testing only!
                updated_now = now + timedelta(minutes=self._speedup)
                time.sleep(1)
            else: 
                updated_now = datetime.now()
            while updated_now < next_run:
                time.sleep((next_run - updated_now).seconds)
            now = next_run
