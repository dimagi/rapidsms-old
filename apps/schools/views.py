from __future__ import absolute_import

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from django.http import HttpResponse
from rapidsms.webui.utils import render_to_response

from schools.models import School

def schools(req):
    return HttpResponse("Schools!")

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