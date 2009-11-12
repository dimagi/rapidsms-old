#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *

import schools.views as views

    
urlpatterns = patterns('',
    url(r'^schools/?$', views.schools),
    url(r'^schools/map/?$', views.map),
    url(r'^schools/xml/?$', views.xml)
)

