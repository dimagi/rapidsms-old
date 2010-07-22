from StringIO import StringIO
from unittest import TestCase
from reporters.models import PersistantBackend, PersistantConnection, Reporter
from messaging.views import parse_csv

class ParseCSVTest(TestCase):
    def test_parse_csv(self):
        self.reporter1 = self._create_reporter('first','1')
        self.reporter2 = self._create_reporter('second','2')
        self.reporter3 = self._create_reporter('third','3')
        csv = "%s, message_to_reporter_1\n %s, message_to_reporter_2\n %s, message_to_reporter_3\n " % \
              (self.reporter1.connection.identity, 
               self.reporter2.connection.identity, 
               self.reporter3.connection.identity)
        input_stream = StringIO(csv)
        returned = parse_csv(input_stream)
        self.assertEqual(returned[0]['reporter'], self.reporter1)
        self.assertEqual(returned[0]['msg'], 'message_to_reporter_1')
        self.assertEqual(returned[1]['reporter'], self.reporter2)
        self.assertEqual(returned[1]['msg'], 'message_to_reporter_2')
        self.assertEqual(returned[2]['reporter'], self.reporter3)
        self.assertEqual(returned[2]['msg'], 'message_to_reporter_3')
        
    def test_error_on_bad_phone_number(self):
        csv = "9898989, message_to_nonexistent_connection"
        input_stream = StringIO(csv)
        self.assertRaises(ValueError, parse_csv, input_stream)
        
    def test_error_on_unregistered_user(self):
        self.connection = self._create_connection("989")
        csv = "%s, message_to_nonexistent_reporter" % self.connection.identity
        input_stream = StringIO(csv)
        self.assertRaises(ValueError, parse_csv, input_stream)
        
    def test_empty_file(self):
        input_stream = StringIO("")
        self.assertRaises(ValueError, parse_csv, input_stream)
        
    def test_poorly_formatted_file(self):
        input_stream = StringIO("junk")
        self.assertRaises(ValueError, parse_csv, input_stream)

    def _create_reporter(self, alias, phone_number):
        reporter = Reporter(alias=alias)
        reporter.save()
        pconnection = self._create_connection(phone_number, reporter)
        reporter.connections.add(pconnection)
        return reporter

    def _create_connection(self, phone_number, reporter=None):
        if not hasattr(self, 'backend'):
            try:
                self.backend = PersistantBackend.objects.get(slug="MockBackend")
            except PersistantBackend.DoesNotExist:
                self.backend = PersistantBackend(slug="MockBackend")
                self.backend.save()
        pconnection = PersistantConnection(backend=self.backend, 
                                                reporter=None, 
                                                identity=phone_number)
        pconnection.save()
        return pconnection
