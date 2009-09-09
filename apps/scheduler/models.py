#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.db import models
from fields import PickledObjectField

# set timespans (e.g. EventSchedule.hours, EventSchedule.minutes) to 
# ALL when we want to schedule something for every hour/minute/etc.
ALL = '*'

class EventSchedule(models.Model):
    """ create a new EventSchedule and save it every time 
    you want to register a new event on a schedule
    we can implement one_off future events by setting count to 1 
    All timespans less than the specified one must be set
    i.e. a weekly schedule must also specify which hour, minute, etc.
    However, all timespans greater than the specified one
    default to "all" (as long as one is specified).
    i.e. a weekly schedule will fire every month
    
    callback - all callback function must take as the first 
        argument a reference to a 'router' object
    """
    description = models.CharField(max_length=255, null=True)
    # how many times do we want this event to fire? optional
    count = models.IntegerField(null=True)
    callback = models.CharField(max_length=255)

    # pickled set
    callback_args = PickledObjectField(null=True)
    # pickled dictionary
    callback_kwargs = PickledObjectField(null=True)

    # the following are pickled sets of numbers
    minutes = PickledObjectField(null=True)
    hours = PickledObjectField(null=True)
    days_of_week = PickledObjectField(null=True)
    days_of_month = PickledObjectField(null=True)
    months = PickledObjectField(null=True)
    
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    
    # First, we must define some utility classes
    class AllMatch(set):
        """Universal set - match everything"""
        def __contains__(self, item): return True
    allMatch = AllMatch(['*'])

    class UndefinedSchedule(TypeError):
        """ raise this error when attempting to save a schedule with a
        greater timespan specified without specifying the lesser timespans
        i.e. scheduling an event for every hour without specifying what
        minute
        """
        pass

    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return "Months:%s Dom:%s Dow:%s Hour:%s Minutes:%s" % \
            ( unicode(self.months),
              unicode(self.days_of_month),
              unicode(self.days_of_week),
              unicode(self.hours),
              unicode(self.minutes) )
            
    def __init__(self, *args, **kwargs):
        super(EventSchedule, self).__init__(*args, **kwargs)
        if self.callback_args is None: self.callback_args = []
        if self.callback_kwargs is None: self.callback_kwargs = {}
        if self.minutes is None: self.minutes = set()
        if self.hours is None: self.hours = set()
        if self.days_of_week is None: self.days_of_week = set()
        if self.days_of_month is None: self.days_of_month = set()
        if self.months is None: self.months = set()
    
    # TODO: define these helper functions
    # def set_daily(self):
    # def set_weekly(self): etc.
    
    def save(self, force_insert=False, force_update=False):
        if not self._valid(self.minutes) or not self._valid(self.hours) or \
            not self._valid(self.days_of_week) or not self._valid(self.days_of_month) or \
            not self._valid(self.months):
            raise TypeError("Minutes/hours/dow/dom/months must specified as sets of numbers")
                
        # when a timespan is set, all sub-timespans must also be set
        # i.e. when a weekly schedule is set, one must also specify day, hour, and minute.
        if len(self.minutes)==0 and len(self.hours)==0 and len(self.days_of_week)==0 and \
            len(self.days_of_month)==0 and len(self.months)==0:
            raise TypeError("Must specify a time interval for schedule")
        if len(self.hours)>0 and len(self.minutes)==0:
            raise self.UndefinedSchedule("Must specify minute(s)")
        if len(self.days_of_week)>0 and len(self.hours)==0: 
            raise self.UndefinedSchedule("Must specify hour(s)")
        if len(self.days_of_month)>0 and len(self.hours)==0: 
            raise self.UndefinedSchedule("Must specify hour(s)")
        if len(self.months)>0 and len(self.days_of_month)==0 and len(self.days_of_week)==0:
            raise self.UndefinedSchedule("Must specify day(s)")
        
        super(EventSchedule, self).save(force_insert, force_update)
    
    def should_fire(self, when):
        """Return True if this event should trigger at the specified datetime """
        if self.start_time:
            if self.start_time > when:
                return False
        if self.end_time:
            if self.end_time < when:
                return False
            
        # The internal variables in this function are because allMatch doesn't 
        # pickle well. This would be alleviated if this functionality were optimized
        # to stop doing db calls on every fire
        minutes = self.minutes
        hours = self.hours
        days_of_week = self.days_of_week
        days_of_month = self.days_of_month
        months = self.months
        if self.minutes == '*': minutes = self.allMatch
        if self.hours == '*': hours = self.allMatch
        if self.days_of_week == '*': days_of_week = self.allMatch
        if self.days_of_month == '*': days_of_month = self.allMatch
        if self.months == '*': months = self.allMatch
        
        # when a timespan is set, all super-timespans default to 'all'
        # i.e. a schedule specified for hourly will automatically be sent
        # every day, week, and month.
        if len(months) == 0:
            months=self.allMatch
        if months == self.allMatch:
            if len(days_of_month)==0:
                days_of_month = self.allMatch
            if len(days_of_week)==0:
                days_of_week = self.allMatch
        if len(hours) == 0 and days_of_month==self.allMatch and \
            days_of_week == self.allMatch:
            hours = self.allMatch
        # self.minutes will never be empty
        
        return ((when.minute     in minutes) and
                (when.hour       in hours) and
                (when.day        in days_of_month) and
                (when.weekday()  in days_of_week) and
                (when.month      in months))

    def _valid(self, timespan):
        if isinstance(timespan, set) or timespan == '*':
            return True
        return False

############################
# global utility functions #
############################

def set_weekly_event(callback, day, hour, minute, callback_args):
    # relies on all the built-in checks in EventSchedule.save()
    schedule = EventSchedule(callback=callback, hours=set([hour]), \
                             days_of_week=set([hour]), minutes=set([minute]), \
                             callback_args=callback_args )
    schedule.save()

def set_daily_event(callback, hour, minute, callback_args):
    # relies on all the built-in checks in EventSchedule.save()
    schedule = EventSchedule(callback=callback, hours=set([hour]), \
                             minutes=set([minute]), \
                             callback_args=callback_args )
    schedule.save()
