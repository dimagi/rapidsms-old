from rapidsms.tests.scripted import TestScript
from rapidsms.message import Message as SmsMessage
from app import App
from models import *
import reporters.app as reporters_app
from reporters.models import Reporter
import datetime

class TestApp (TestScript):
    apps = (reporters_app.App, App)

    def testBasic(self):
        script = """
            sample_1 > here is a message
            sample_1 > here is another message!
            sample_2 > here is a third message... 
        """
        self.runScript(script)
        connection = PersistantConnection.objects.all()[0]
        be = self.router.get_backend(connection.backend.slug)
        be.message(connection.identity, "This is an outgoing message!").send()
        self.assertEqual(4, Message.objects.count())
        self.assertEqual(3, Message.objects.filter(is_incoming=True).count())
        self.assertEqual(1, Message.objects.filter(is_incoming=False).count())
        