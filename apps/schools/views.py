from django.http import HttpResponse
from rapidsms.webui.utils import render_to_response

def schools(req):
    return HttpResponse("Schools!")

def map(req, template_name="schools/school_map.html"):
    """Display a map with school data on it"""
    return render_to_response(req, template_name, {})

def xml(req, template_name="schools/demo.xml"):
    """Get some basic xml data for populating the map."""
    return render_to_response(req, template_name, {})