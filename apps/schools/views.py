from __future__ import absolute_import

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rapidsms.webui.utils import render_to_response

from schools.models import *

def schools(req, template_name="schools/summary.html"):
    schools = School.objects.all()
    return render_to_response(req, template_name, { "schools": schools })


def map(req, template_name="schools/school_map.html"):
    """Display a map with school data on it"""
    return render_to_response(req, template_name, {})

def xml(req, template_name="schools/demo.xml"):
    """Get some basic xml data for populating the map."""
    all_schools = School.objects.all()
    root = Element("root")
    for school in all_schools:
        school_elem = school.to_element()
        root.append(school_elem)
    return HttpResponse(ElementTree.tostring(root), mimetype="text/xml")

def single_school(req, id, template_name="schools/single_school.html"):
    school = get_object_or_404(School, id=id)
    return render_to_response(req, template_name, { "school": school })

def message(req, id, template_name="schools/message.html"):
    head = get_object_or_404(Headmaster, id=id)
    return render_to_response(req, template_name, { "reporter": head })

def headmasters(req, template_name="schools/headmasters.html"):
    all = Headmaster.objects.all()
    return render_to_response(req, template_name, { "headmasters": all})