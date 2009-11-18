from django.db import models

from reporters.models import Reporter
from schools.models import Headmaster

class BlastableMessage(models.Model):
    """A message that can be blasted."""
    text = models.CharField(max_length=160)
    
    # todo: parsing, validation.  Could potentially use the Questions app
    # for this.
    
    def __unicode__(self):
        return self.text

class MessageBlast(models.Model):
    """An instance of blasting a message to multiple people.
       Only one blast can remain open per-person."""
    message = models.ForeignKey(BlastableMessage)
    date = models.DateTimeField()

    def responded(self):
        """Get a list of who has responded to this."""
        recipients = self.recipients.all()
        return [recipient for recipient in recipients if recipient.responded > 0]
                
    def successfully_responded(self):
        """Get a list of who has _successfully_ responded to this."""
        recipients = self.recipients.all()
        return [recipient for recipient in recipients \
                if recipient.successfully_responded]
    
class BlastedMessage(models.Model):
    """The message that was blasted"""
    blast = models.ForeignKey(MessageBlast, related_name="recipients")
    reporter = models.ForeignKey(Reporter)
    
    
    @classmethod
    def current(cls, reporter):
        reporter_msgs = cls.objects.filter(reporter=reporter)
        if reporter_msgs:
            latest = reporter_msgs.order_by("-blast__date")[0]
            # it's only current if it doesn't yet have a successful
            # response.  All other paths return nothing.
            if not latest.successfully_responded:
                return latest
        
        
    @property 
    def school(self):
        try:
            return Headmaster.objects.get(id=self.reporter.id).school
        except Headmaster.DoesNotExist:
            return None
            
    @property
    def responded (self):
        return self.responses.count() > 0
    
    @property
    def successfully_responded (self):
        return self.responses.filter(success=True).count() > 0
    
    def status(self):
        if self.successfully_responded:
            return "success"
        elif self.responded:
            return "responded"
        else:
            return "pending"
        
    @property
    def response(self):
        """Get the default response (the most recent one)"""
        if self.responded:
            return self.responses.order_by('-date')[0]
        
    
class BlastResponse(models.Model):
    """Any responses to a blast."""
    message = models.ForeignKey(BlastedMessage, related_name="responses")
    date = models.DateTimeField(null=True, blank=True)
    text = models.CharField(max_length=160)
    success = models.BooleanField()
    