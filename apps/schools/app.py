import rapidsms

from schools.models import *

class App (rapidsms.app.App):
    
    def start (self):
        """Configure your app in the start phase."""
        pass

    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        # stick a headmaster on here, if we find her.  Otherwise 
        # just set the property empty
        message.headmaster = None
        if message.reporter:
            try:
                message.headmaster = Headmaster.objects.get(id=message.reporter.id)
            except Headmaster.DoesNotExist:
                pass


    def handle (self, message):
        """Add your main application logic in the handle phase."""
        pass

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

    def teacher_attendance(self, msg):
        """Handles teacher attendance"""
        if msg.headmaster:
            if msg.text.isdigit():
                teacher_count = int(msg.text)
                school = msg.headmaster.school
                SchoolTeacherReport.objects.create(reporter=msg.headmaster,
                                                   date=msg.date,
                                                   school=school,
                                                   expected=school.teachers,
                                                   actual=teacher_count)
                msg.respond("Thank you for your report of %s teachers attending %s today, %s!" %\
                            (teacher_count, school, msg.headmaster))
                return True
            else:
                msg.respond("Sorry %s, I didn't understand %s. Just send the number of teachers who attended school today." %\
                            (msg.headmaster, msg.text))
        elif msg.reporter:
            # should be impossible
            msg.respond("Sorry, %s but we can't find which school you are a headmaster of." %\
                        (msg.reporter))
        else:
            # should be impossible
            msg.respond("Sorry, but we don't know who you are!")
                        
                
                                                   
                