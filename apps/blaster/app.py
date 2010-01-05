from datetime import datetime

import rapidsms

from blaster.models import *

class App (rapidsms.app.App):
    """From the view, conduct a message blast.  Responses get collected
       with the blast.  Only one blast can be open at a given time."""
    
    def handle (self, message):
        """Add your main application logic in the handle phase."""
        if not message.reporter:
            # couldn't have been intended for us
            return
        
        latest = BlastedMessage.current(message.reporter)
        if latest:
            response = BlastResponse.objects.create(message=latest,
                                                    text=message.text,
                                                    date=datetime.now(),
                                                    success=True)
            return True
        
