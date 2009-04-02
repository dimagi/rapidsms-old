#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import django
from django.db import models


class MessageBase(models.Model):
    text = models.CharField(max_length=140)
    caller = models.CharField(max_length=15)
	# TODO save backend title rather than wacky object string?
    backend = models.CharField(max_length=150)
    
    def __unicode__(self):
        return "[%s (%s)] %s" % (self.caller, self.backend, self.text)
    
    class Meta:
        abstract = True
    
    
class IncomingMessage(MessageBase):
    received = models.DateTimeField(auto_now_add=True)
    

class OutgoingMessage(MessageBase):
    sent = models.DateTimeField(auto_now_add=True)