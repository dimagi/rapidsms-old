#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from __future__ import absolute_import
from rapidsms.message import Message, EmailMessage
from rapidsms.connection import Connection
from . import backend
import imaplib
import time
import smtplib
import re

from datetime import datetime
from email import message_from_string
from email.mime.text import MIMEText

class Backend(backend.Backend):
    '''Uses the django mail object utilities to send outgoing messages
       via email.  Messages can be formatted in standard smtp, and these
       parameters will end up going into the subject/to/from of the
       email.  E.g.
       ==
       
       Subject: Test message

       Hello Alice.
       This is a test message with 5 header fields and 4 lines in the message body.
       Your friend,
       Bob
       
       ==
       
       The following defaults are currently used in place of the expected
       fields from smtp:
       
       From: <configured login>
       To: <connection identity>
       Date: <datetime.now()>
       
    '''
    _title = "Email"
    _connection = None
    POLL_INTERVAL = 10
    
    def configure(self, smtp_host="localhost", smtp_port=25,  
                  imap_host="localhost", imap_port=143,
                  username="demo-user@domain.com",
                  password="secret", 
                  use_tls=True):
        # the default information will not work, users need to configure this
        # in their settings
        
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._imap_host = imap_host
        self._imap_port = imap_port
        self._username = username 
        self._password = password
        self._use_tls = use_tls 
        
    def send(self, email_message):
        # Create a text/plain message for now
        msg = MIMEText(email_message.text)

        msg['Subject'] = getattr(email_message, "subject", None)
        msg['From'] = self._username 
        msg['To'] = email_message.peer
        
        print "sending mail: %s" % email_message.text
        if self._use_tls:
            s = smtplib.SMTP_SSL(host=self._smtp_host, port=self._smtp_port)
        else:
            s = smtplib.SMTP(host=self._smtp_host, port=self._smtp_port)
            
        s.login(self._username, self._password)
        s.sendmail(self._username, [email_message.peer], msg.as_string())
        s.quit()
        print "finished sending mail"
        
        
    def start(self):
        backend.Backend.start(self)

    def stop(self):
        backend.Backend.stop(self)
        self.info("Shutting down...")

    
    def run(self):
        while self._running:
            # check for new messages
            messages = self._get_new_messages()
            if messages:
                for message in messages:
                    self.router.send(message)
            time.sleep(self.POLL_INTERVAL)
            
    def _get_new_messages(self):
        print "fetching mail"
        imap_connection = imaplib.IMAP4_SSL(self._imap_host, self._imap_port)
        imap_connection.login(self._username, self._password)
        imap_connection.select()
        all_msgs = []
        # this assumes any unread message is a new message
        typ, data = imap_connection.search(None, 'UNSEEN')
        for num in data[0].split():
            typ, data = imap_connection.fetch(num, '(RFC822)')
            # get a rapidsms message from the data
            email_message = self._message_from_imap(data[0][1])
            all_msgs.append(email_message)
            # mark it read
            imap_connection.store(num, "+FLAGS", "\\Seen")
        imap_connection.close()
        imap_connection.logout()
        print "finished fetching mail"
        return all_msgs
    
    def _message_from_imap(self, imap_mail):
        parsed = message_from_string(imap_mail)
        from_user = parsed["From"] 
        subject = parsed["Subject"]
        date_string = parsed["Date"]
        # until we figure out how to generically parse dates, just use
        # the current time
        # truncated_date = date_string[0:len(date_string) - 12]
        # date = datetime.strptime(truncated_date, "%a, %d %b %Y %H:%M:%S")
        date = datetime.now()
        connection = Connection(self, from_user)
        message_body = self._get_message_body(parsed)
        msg = EmailMessage(connection=connection, text=message_body, 
                           date=date, subject=subject)
        return msg
    
    def _is_plaintext(self, email_message):
        return re.match("text/plain", email_message.get_content_type(), re.IGNORECASE)
    
    def _is_text(self, email_message):
        return re.match("text/*", email_message.get_content_type(), re.IGNORECASE)
    
    def _get_message_body(self, email_message):
        """Walk through the message parts, taking the first text/plain.
           if no text/plain (is this allowed?) will return the first
           text/html"""
        candidate = None
        if email_message.is_multipart():
            for message_part in email_message.walk():
                if self._is_plaintext(message_part):
                    return message_part.get_payload()
                elif self._is_text(message_part):
                    candidate = message_part
        if candidate == None:
            # what to do?  
            self.error("Got a poorly formed email")
            return ""
        return candidate.get_payload()
