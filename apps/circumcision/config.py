'''
Created on Apr 8, 2010

@author: Drew Roos
'''

incoming_tz = 'Africa/Nairobi'
server_tz = 'America/New_York' #todo: should find a way to set this automatically;
                               #actually not needed at all if scheduler were able to run off UTC
                               #or an arbitrary timezone

notification_days = [1, 2, 3, 4, 5, 6, 7, 8, 14, 21, 28, 35, 41, 42]

default_language = 'en'
itext = {
    'en': {
        'reg-keyword': 'register',
        'reg-success': 'You have been registered. You will receive your notifications at %s',
        'cannot-parse': 'Did not understand; send message as: register [patient id] [desired contact time (HHMM)]',
        'patid-unrecognized': 'Do not recognize patient ID',
        'already-registered': 'You have already been registered. You registered on %s',
        'phone-already-registered': 'This patient ID has already been registered on another phone',
        'patid-already-registered': 'This phone has already been registered for another patient',
        'cannot-parse-time': 'Did not understand contact time; send as HHMM, i.e., 0600 for 6 AM or 2030 for 8:30 PM',
        'notif1': 'notification for day 1',
        'notif2': 'notification for day 2',
        'notif3': 'notification for day 3',
        'notif4': 'notification for day 4',
        'notif5': 'notification for day 5',
        'notif6': 'notification for day 6',
        'notif7': 'notification for day 7',
        'notif8': 'notification for day 8',
        'notif14': 'notification for day 14',
        'notif21': 'notification for day 21',
        'notif28': 'notification for day 28',
        'notif35': 'notification for day 35',
        'notif41': 'notification for day 41',
        'notif42': 'notification for day 42',
    }
}
