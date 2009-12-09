#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms
import re


class App(rapidsms.app.App):
    """
    Grab all incoming messages, and respond with something appropriate.
    Use this to make ministers feel all warm and fuzzy about RapidSMS.
    """

    def handle(self, msg):
        txt = msg.text

        if re.search(r"join", txt, re.I):
            resp = "Thank you for joining RapidSMS!"

        elif re.search(r"report", txt, re.I):
            resp = "Thank you for submitting a report to RapidSMS!"

        elif re.search(r"help", txt, re.I):
            resp = "Help: To join RapidSMS, respond JOIN <YOUR NAME>. To send a report, respond REPORT <YOUR MESSAGE>"

        else:
            resp = "Thank you for trying RapidSMS! I'm sorry, but I did not understand your message."

        msg.respond(resp)
        return True
