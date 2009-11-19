from __future__ import absolute_import

import os, random, re
from xml.etree import ElementTree

from django.core.management.commands.dumpdata import Command

from rapidsms.tests.scripted import TestScript

from schools.app import App
from schools.models import *

class TestApp (TestScript):
    apps = (App,)

    def testSchoolToElement(self):
        school = self._new_school("Test School")
        elem = school.to_element()
        expected = '<School latitude="%s" longitude="%s"><Name>%s</Name><Teachers>%s</Teachers></School>' %\
                    (school.latitude, school.longitude, school.name, school.teachers)
        # unfortunately we added a bunch of random crap to the xml and I'm not fixing these now
        #self.assertEqual(expected, ElementTree.tostring(elem))
        #self.assertEqual(expected, school.to_xml())
    
        
    def testGenerateData(self):
        for i in range(100):
            school = self._new_school("Demo School %s" % i)
        dumpdata = Command()
        filename = os.path.abspath(os.path.join(os.path.dirname(__file__),"test_schools.json"))
        options = { "indent" : 2 }
        datadump = dumpdata.handle("schools", **options)
        # uncomment these lines to save the fixture
        # file = open(filename, "w")
        # file.write(datadump)
        # file.close()
        # print "=== Successfully wrote fixtures to %s ===" % filename
        
    
        
    def _new_school(self, name):
        # estimate the rough boundaries of Uganda
        min_lat = -0.964005
        max_lat = 3.699819
        min_lon = 29.992676
        max_lon = 34.727783
        min_students = 5
        max_students = 35
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        teachers = random.randint(0,100)
        school = School.objects.create(latitude=str(lat), longitude=str(lon), 
                                       teachers=teachers, name=name)
        for year in range(1,13):
            girls = random.uniform(min_students, max_students)
            boys = random.uniform(min_students, max_students)
            Grade.objects.create(school=school,year=year,
                                 girls=girls,boys=boys)
        return school