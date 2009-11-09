from django.http import HttpResponse

def schools(req):
    return HttpResponse("Schools!")