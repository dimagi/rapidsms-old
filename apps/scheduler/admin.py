#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.contrib import admin
from scheduler.models import EventSchedule

admin.site.register(EventSchedule)
