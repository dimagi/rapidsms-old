from __future__ import absolute_import

import math
import random

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from django.db import models

from reporters.models import Reporter
from schools.xml import SerializableModel


class School(models.Model,SerializableModel):
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
             "WaterAvailability": "water_availability"
              }
        
    latitude  = models.DecimalField(max_digits=8, decimal_places=6, 
                                    blank=True, null=True, 
                                    help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=8, decimal_places=6, 
                                    blank=True, null=True, 
                                    help_text="The physical longitude of this location")

    name = models.CharField(max_length=200)
    
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
    def teacher_attendance(self):
        """Get total teacher attendance rate"""
        #todo
        return random.randint(0, 100)
    
    @property
    def student_attendance(self):
        """Get total student attendance rate"""
        #todo
        return random.randint(0, 100)
    
    @property
    def boys_attendance(self):
        """Get total boys attendance rate"""
        #todo
        return random.randint(0, 100)
    
    @property
    def girls_attendance(self):
        """Get total girls attendance rate"""
        #todo
        return random.randint(0, 100)
    
    @property
    def water_availability(self):
        """Get total girls attendance rate"""
        #todo
        return random.randint(0, 100)
            
class Headmaster(Reporter):
    """A headmaster of a school"""
    
    school = models.ForeignKey(School)
    
    def __unicode__(self):
        return Reporter.__unicode__(self)
    
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
    school = models.ForeignKey(School)
    # this will be pulled from the school's information at the time of submitting
    # to allow that to change over time
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()
    
    def percent(self):
        if self.expected != 0:
            return self.actual / self.expected
        return "N/A"
        
    
class SchoolWaterReport(Report):
    """Report of school water information on a particular day"""
    school = models.ForeignKey(School)
    water_working = models.BooleanField()
    
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
    
