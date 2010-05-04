#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ['connection', 'is_incoming', 'text', 'date']
    list_filter = ['connection', 'is_incoming', 'text', 'date']
    date_hierarchy = 'date'

admin.site.register(Message, MessageAdmin)
