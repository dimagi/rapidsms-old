from __future__ import absolute_import, division

import math
import random

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from django.db import models

from locations.models import Location, LocationType
from reporters.models import Reporter, ReporterGroup
from schools.xml import SerializableModel


class School(Location,SerializableModel):
    """A basic model for a school."""
    # these two fields determine how the model is displayed as XML
    # the key is the name of the attribute/element, the value is
    # the field/property used to display it.  
    ATTRS = {"latitude": "latitude",
             "longitude": "longitude"}
    
    ELEMS = {"Name": "name", 
             "Teachers": "teachers",
             "Headmaster": "headmaster",
             "TeacherAttendance": "teacher_attendance",
             "StudentAttendance": "student_attendance",
             "BoysAttendance": "boys_attendance",
             "GirlsAttendance": "girls_attendance",
             "WaterAvailability": "water_availability",
             "ResponseRate": "response_rate"
              }
    
    teachers = models.PositiveIntegerField(help_text="The number of teachers at the school")
    
    
    
    def __unicode__(self):
        return self.name
    
    @property
    def headmaster(self):
        try:
            return Headmaster.objects.get(school=self)
        except Headmaster.DoesNotExist:
            return None
        except Headmaster.MultipleObjectsReturned:
            # todo: determine if we want to handle this better.
            return Headmaster.objects.filter(school=self)[0]
    
    @property
    def response_rate(self):
        """Get response rate for this schools headmaster."""
        headmaster = self.headmaster
        if headmaster:
            # too lazy to clean the circular imports now
            from blaster.models import BlastResponse, BlastedMessage
            success = BlastResponse.\
                        objects.filter(message__reporter=headmaster,
                                       success=True).count()
            tried = BlastedMessage.\
                        objects.filter(reporter=headmaster).count()
            if tried != 0:
                return success/tried * 100
        return "No data"
        
    @property
    def teacher_attendance(self):
        """Get total teacher attendance rate"""
        reports = SchoolTeacherReport.objects.filter(school=self)
        if not reports: return "No data"
        return self._percent_expected_actual(reports)
        
    @property
    def student_attendance(self):
        """Get total student attendance rate"""
        boys_reports = BoysAttendenceReport.objects.filter(grade__school=self)
        girls_reports = GirlsAttendenceReport.objects.filter(grade__school=self)
        if not boys_reports and not girls_reports: return "No data"
        return self._percent_expected_actual(boys_reports, girls_reports)
    
    @property
    def boys_attendance(self):
        """Get total boys attendance rate"""
        reports = BoysAttendenceReport.objects.filter(grade__school=self)
        if not reports: return "No data"
        return self._percent_expected_actual(reports)
    
    
    @property
    def girls_attendance(self):
        """Get total girls attendance rate"""
        reports = GirlsAttendenceReport.objects.filter(grade__school=self)
        if not reports: return "No data"
        return self._percent_expected_actual(reports)
        
    @property
    def water_availability(self):
        """Get total girls attendance rate"""
        reports = SchoolWaterReport.objects.filter(school=self)
        if not reports: return "No data"
        return self._percent_expected_actual(reports)
        
    
    def _percent_expected_actual(self, *args):
        expected = 0
        actual = 0
        for arg in args:
            expected = expected + sum([report.expected for report in arg])
            actual = actual + sum([report.actual for report in arg])
        if expected != 0:
            return actual / expected * 100
        else:
            return "Error, divide by 0?"
        
            
class Headmaster(Reporter):
    """A headmaster of a school"""
    
    school = models.ForeignKey(School)
    
    def __unicode__(self):
        return Reporter.__unicode__(self)
    
class SchoolGroup(ReporterGroup):
    """A group of reporters attached to a school."""
    # this enum takes the form 
    # { <key>: (group display, member display) }
    # the group displays are used by django 
    SCHOOL_GROUP_TYPES = {
        'GEM': ('GEM Leaders', 'GEM Leader'),
        'PTA': ('Parent-Teachers Association', 'PTA Member'),
        'Teachers': ('Teachers', 'Teacher'),
        'Headmasters': ('Headmasters', 'Headmaster') # this is kind of redundant with the existing headmaster
    }
    GROUP_ENUMS = ((key, values[0]) for key, values in SCHOOL_GROUP_TYPES.items())
    type = models.CharField(max_length=20, choices=GROUP_ENUMS)
    school = models.ForeignKey(School, related_name="groups")
    
    def members_list_display(self):
        """A display string for the list of members."""
        return ", ".join([str(reporter) for reporter in self.reporters.all()])
    
    def member_title(self):
        """The title that this groups members go by E.g. members of the 
           Parent Teachers Association group are known as PTA Members."""
        return self.SCHOOL_GROUP_TYPES[self.type][1]

    def group_title(self):
        """The title that this group is known by."""
        return self.get_type_display()
        
    def __unicode__(self):
        return "%s %s" % (self.school,self.type)
                                       
class Grade(models.Model):
    """A Grade (class) in a school"""
    school = models.ForeignKey(School, related_name="classes")
    year = models.PositiveIntegerField(help_text="1-12")
    boys = models.PositiveIntegerField(help_text="Number of boys in the class")
    girls = models.PositiveIntegerField(help_text="Number of girls in the class")
    
    def __unicode__(self):
        return "%s - Grade %s" % (self.school, self.year)

class Report(models.Model):
    """A reporting of some information"""
    date = models.DateTimeField()
    reporter = models.ForeignKey(Headmaster)
    
    class Meta:
        abstract = True

class SchoolTeacherReport(Report):
    """Report of school teacher attendance on a particular day"""
    school = models.ForeignKey(School, related_name="teacher_attendance_reports")
    # this will be pulled from the school's information at the time of submitting
    # to allow that to change over time
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()
    
    def percent(self):
        if self.expected != 0:
            return self.actual / self.expected * 100
        return "N/A"
        
    def __unicode__(self):
        return "%s of %s teachers at %s" % (self.actual, self.expected, self.school)
    
class SchoolWaterReport(Report):
    """Report of school water information on a particular day"""
    school = models.ForeignKey(School, related_name="water_reports")
    water_working = models.BooleanField()
    
    @property
    def expected(self):
        # allows us to fake treat these like everything else
        return 100
    
    @property
    def actual(self):
        # allows us to fake treat these like everything else
        return 100 if self.water_working else 0
    
    
class BoysAttendenceReport(Report):
    """Report of grade/classroom attendance on a particular day"""
    grade = models.ForeignKey(Grade)
    # this will be pulled from the grade's information at the time of submitting
    # to allow that to change over time
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()

class GirlsAttendenceReport(Report):
    """Report of grade/classroom attendance on a particular day"""
    grade = models.ForeignKey(Grade)
    # this will be pulled from the grade's information at the time of submitting
    # to allow that to change over time
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()

class SchoolReport(Report):
    """Any other (unanticipated) report having to do with a school"""     
    school = models.ForeignKey(School)
    question = models.CharField(max_length=160) # todo: foreign key question 
    answer = models.CharField(max_length=160) # todo: foreign key answer
    
class GradeReport(Report):
    """Any other (unanticipated) report having to do with a grade"""     
    grade = models.ForeignKey(Grade)
    question = models.CharField(max_length=160) # todo: foreign key question 
    answer = models.CharField(max_length=160) # todo: foreign key answer
    
