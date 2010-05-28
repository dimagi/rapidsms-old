'''
Created on Mar 31, 2010

@author: Drew Roos
'''

import rapidsms
import logging
from circumcision.models import *
import circumcision.config as config
from scheduler.models import set_daily_event, EventSchedule
from datetime import datetime, timedelta, time
import pytz
import messaging.app

def text (key, lang):
    """return a localized text string for a given text key and language code"""
    if lang not in config.itext:
        raise ValueError('no language [%s] defined' % lang)
    elif key not in config.itext[lang]:
        raise ValueError('no translation for key [%s] in language [%s]' % (key, lang))
    else:
        return config.itext[lang][key]

def get_notification (day, lang):
    """return the notification text for day N"""
    return text('notif%d' % day, lang)

def split_contact_time (minutes_since_midnight):
    """split the 'minutes since midnight' contact time into hour and minute components"""
    m = int(minutes_since_midnight)
    return (m / 60, m % 60)

class App (rapidsms.app.App):

    def start (self):
        """Configure your app in the start phase."""
        self.verify_config()

    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass

    def handle (self, message):
        try:
            (patient_id, contact_time, lang) = self.parse_message(message)
        except ValueError, response:
            message.respond(response)
            return True
        connection = message.persistant_connection
        
        reg = Registration(patient_id=patient_id, contact_time=contact_time, connection=connection, language=lang)
        reg.save()
        
        self.schedule_notifications(reg, message.date)
        
        message.respond(text('reg-success', lang) % ('%02d:%02d' % split_contact_time(contact_time)))
        return True

    def parse_message (self, message):
        """parse the sms message, either raising a variety of exceptions, or returning patient id,
        contact time as integer minutes since midnight, and language code to use for future notifications"""
        pieces = message.text.split()
        
        #discriminate language based on 'register' keyword?
        if len(pieces) < 3 or pieces[0] != text('reg-keyword', config.default_language):
            raise ValueError(text('cannot-parse', config.default_language))
        lang = config.default_language
        
        patient_id = pieces[1]
        contact_time_str = pieces[2]
        
        if not self.validate_patient_id_format(patient_id):
            raise ValueError(text('patid-unrecognized', lang))
        
        #check if patient has already been registered
        try:
            reg = Registration.objects.get(patient_id=patient_id)
            patid_already_registered = True
        except Registration.DoesNotExist:
            patid_already_registered = False
        
        #check if phone number has already been registered
        try:
            Registration.objects.get(connection=message.persistant_connection)
            phone_already_registered = True
        except Registration.DoesNotExist:
            phone_already_registered = False
    
        #todo: change behavior if existing registration is completed/expired
        if patid_already_registered:
            if phone_already_registered:
                raise ValueError(text('already-registered', lang) % reg.registered_on.strftime('%d-%m-%Y'))
            else:
                raise ValueError(text('patid-already-registered', lang))
        elif phone_already_registered:
            raise ValueError(text('phone-already-registered', lang))
        
        contact_time = self.parse_contact_time(contact_time_str)
        if contact_time == None:
            raise ValueError(text('cannot-parse-time', lang))
        
        return (patient_id, contact_time, lang)

    #todo: should normalize patient id here too, if applicable
    def validate_patient_id_format(self, patient_id):
        """validate and normalize the patient id"""
        return True
        
    def parse_contact_time (self, contact_time_str):
        """parse the contact time and return a normalized value of minutes since midnight"""
        if len(contact_time_str) != 4:
            return None
        
        try:
            hour = int(contact_time_str[0:2])
            minute = int(contact_time_str[2:4])
        except ValueError:
            return None
        
        if hour < 0 or hour >= 24 or minute < 0 or minute >= 60:
            return None
        
        return hour * 60 + minute
    
    def schedule_notifications (self, reg, reg_time):
        """schedule all future notificaitons to be sent for this patient"""
        for day in config.notification_days:
            send_at = self.calc_send_time(reg_time, reg.contact_time, day)
            #scheduler works in local server time instead of UTC
            local_send_at = send_at.astimezone(pytz.timezone(config.server_tz)).replace(tzinfo=None)
            
            schedule = EventSchedule(callback="circumcision.app.send_notification", \
                                     start_time=local_send_at, count=1, minutes='*',
                                     callback_args=[reg.patient_id, day, reg.language],
                                     description='patient %s; day %d' % (reg.patient_id, day))
            schedule.save()

    def calc_send_time (self, reg_time, contact_time, day):
        """Given the date/time of registration, and the daily contact time, return the
        UTC timestamp to send the notification for day N
        
        reg_time: timestamp of registration; naked datetime, UTC
        contact_time: time of day to send; int minutes from midnight
        day: number of days after day of registration that message is being sent
        """
        
        local_tz = pytz.timezone(config.incoming_tz)
        reg_time = pytz.utc.localize(reg_time)
        reg_time_local = reg_time.astimezone(local_tz)
        reg_date = reg_time_local.date()
        send_date = reg_date + timedelta(days=day)
        send_time = time(*split_contact_time(contact_time))
        send_time_local = datetime.combine(send_date, send_time)
        send_at = local_tz.localize(send_time_local).astimezone(pytz.utc)
        return send_at
    
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
        
    def verify_config (self):
        """perform some basic validation for the config, namely that notifications for all days are
        defined in all languages"""
        if config.default_language not in config.itext:
            raise ValueError('default language [%s] not defined' % config.default_language)
        
        for lang in config.itext.keys():
            for day in config.notification_days:
                try:
                    get_notification(day, lang)
                except ValueError:
                    raise ValueError('no notification set for day %d in language [%s]' % (day, lang))
        

def send_notification (router, patient_id, day, lang):
    """send the notification for day N"""
    reg = Registration.objects.get(patient_id=patient_id)
    router.get_app('messaging')._send_message(reg.connection, get_notification(day, lang))
    #check for success?
    
    log = SentNotif(patient_id=reg, day=day)
    log.save()
