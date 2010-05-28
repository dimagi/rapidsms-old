'''
Created on Mar 31, 2010

@author: Drew Roos
'''

import circumcision.views as views
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^circumcision/$', views.patient_list),
    url(r'^circumcision/patient/(.+)/$', views.patient_update),
)