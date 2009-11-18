import re

import rapidsms

from schools.models import *

class App (rapidsms.app.App):
    TRUE  = re.compile(r"^(?:[YT].*|1)$", re.IGNORECASE)
    FALSE = re.compile(r"^(?:[NF].*|0)$", re.IGNORECASE)
    
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
    
    
    def get_headmaster_or_respond(self, msg):
        """Gets the headmaster from the message, or responds if there isn't one"""
        if msg.headmaster:
            return msg.headmaster
        elif msg.reporter:
            # should be impossible
            msg.respond("Sorry %s, but we can't find which school you are a headmaster of." %\
                        (msg.reporter))
        else:
            # should be impossible
            msg.respond("Sorry, but we don't know who you are!")
        
    def get_grade_or_respond(self, msg, headmaster, grade_year):
        """Gets the grade for the school and grade number, or responds if there isn't one"""
        try:
            return Grade.objects.get(school=headmaster.school, year=grade_year)
        except Grade.DoesNotExist:
            msg.respond("Sorry %s, but we can't find a Grade %s class at %s." %\
                        (headmaster, grade_year, headmaster.school))

    def teacher_attendance(self, msg):
        """Handles teacher attendance"""
        headmaster = self.get_headmaster_or_respond(msg)
        if headmaster:
            if msg.text.isdigit():
                teacher_count = int(msg.text)
                school = headmaster.school
                SchoolTeacherReport.objects.create(reporter=headmaster,
                                                   date=msg.date,
                                                   school=school,
                                                   expected=school.teachers,
                                                   actual=teacher_count)
                msg.respond("Thank you for your report of %s teachers attending %s today, %s!" %\
                            (teacher_count, school, headmaster))
                return True
            else:
                msg.respond("Sorry %s, I didn't understand %s. Just send the number of teachers who attended school today." %\
                            (msg.headmaster, msg.text))
                

    def grade_attendance(self, msg, grade_year=1):
        """Handles teacher attendance"""
        headmaster = self.get_headmaster_or_respond(msg)
        if not headmaster: return
        grade = self.get_grade_or_respond(msg, headmaster, grade_year)
        if not grade: return
        
        def fail(msg, headmaster):
            """This message gets sent if anything goes wrong""" 
            msg.respond("Sorry, %s, we couldn't understand that. Please send a message like: 4 boys 5 girls." %\
                        headmaster)
            
        # we expect "5 girls, 3 boys"
        # or "12 g 9 b"
        # this code is really dumb, but we're just going to split into
        # 4 parts, assume 1 + 3 are digits, and filter 2 + 4 based on the
        # first letter.  
        groups = msg.text.split(" ")
        if len(groups) >= 4:
            if groups[0].isdigit() and groups[2].isdigit():
                if groups[1].lower().startswith("b") and groups[3].lower().startswith("g"):
                    boys = int(groups[0])
                    girls = int(groups[2])
                elif groups[1].lower().startswith("g") and groups[3].lower().startswith("b"):
                    girls = int(groups[0])
                    boys = int(groups[2])
                else:
                    fail(msg, headmaster)
                
                GirlsAttendenceReport.objects.create(reporter=headmaster,
                                                     date=msg.date,
                                                     grade=grade,
                                                     expected=grade.girls,
                                                     actual=girls)
                BoysAttendenceReport.objects.create(reporter=headmaster,
                                                    date=msg.date,
                                                    grade=grade,
                                                    expected=grade.boys,
                                                    actual=boys)
                                    
                
                msg.respond("Thank you for your report of %s girls and %s boys attending %s today, %s!" %\
                            (girls,boys, headmaster.school, headmaster))
                return True
        fail(msg, headmaster)
            
                                                   
    def water_availability(self, msg):
        """Handles water availability"""
        
        headmaster = self.get_headmaster_or_respond(msg)
        if not headmaster: return 
        
        def fail(msg, headmaster):
            """This message gets sent if anything goes wrong""" 
            msg.respond("Sorry, %s, we couldn't understand that. Please send a message like: 4 boys 5 girls." %\
                        headmaster)
        
        if self.TRUE.match(text):    water = True  
        elif self.FALSE.match(text): water = False
        else:                        
            fail()
            return
        
            