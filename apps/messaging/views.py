#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re, urllib
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import FieldError
from django.core.urlresolvers import reverse
from rapidsms.webui.utils import *
from reporters.models import *
from models import combined_message_log, __combined_message_log_row


def index(req):
    return _messaging(req)

def groups(req):
    return _messaging(req, groups=True)

def _messaging(req, groups=False):
    def cookie_recips(status):
        flat = urllib.unquote(req.COOKIES.get("recip-%s" % status, ""))
        return map(int, re.split(r'\s+', flat)) if flat != "" else []

    checked  = cookie_recips("checked")
    error    = cookie_recips("error")
    sent     = cookie_recips("sent")

    show_search = False
    filtered    = False
    hits        = []

    def __decorate(obj):
        # this can decorate a reporter or group - anything in the UI
        obj.is_checked = obj.pk in checked
        obj.is_error   = obj.pk in error
        obj.is_sent    = obj.pk in sent
        obj.is_hit     = obj.pk in hits
        return obj

    # set a few obects so we can deal with reporters and groups
    # through the same utility code and templates.
    
    # Instead of referencing the model, we do it through this
    # variable, allowing us to be agnostic about whether we're talking
    # about reporters or groups.
    model_class = ReporterGroup if groups else Reporter
    item_template = "messaging/partials/group.html" if groups \
                    else "messaging/partials/reporter.html"
    headers = ("Title", "Description", "Members") if groups \
              else ("Name", "Role", "Location") 
    post_url = "/ajax/messaging/group_message" if groups \
               else "/ajax/messaging/send_message"
    
    # if the field/cmp/query parameters were provided (ALL
    # OF THEM), we will mark some of the reporters as HIT
    if "query" in req.GET or "field" in req.GET or "cmp" in req.GET:
        if "query" not in req.GET or "field" not in req.GET or "cmp" not in req.GET:
            return HttpResponse("The query, field, and cmp fields may only be provided or omitted TOGETHER.",
                status=500, mimetype="text/plain")

        # search with: field__cmp=query
        kwargs = { str("%s__%s" % (req.GET["field"], req.GET["cmp"])): req.GET["query"] }
        hits = model_class.objects.filter(**kwargs).values_list("pk", flat=True)
        show_search = True
        filtered = True

    # optionally show the search field as default
    if "search" in req.GET and req.GET["search"]:
        show_search = True

    # the columns to display in the "field"
    # field of the search form. this is WAY
    # ugly, and should be introspected
    if not groups:
        columns = [
                   ("alias", "Alias"),
                   ("first_name", "First Name"),
                   ("last_name", "Last Name")]#,
            #("role__title", "Role"),
            #("location__name", "Location")]
    else:
        columns = [("title", "Title"),
                   ("description", "Description")]
                   

    resp = render_to_response(req,
        "messaging/index.html", {
            "columns":     columns,
            "filtered":    filtered,
            "query":       req.GET.get("query", ""),
            "field":       req.GET.get("field", ""),
            "cmp":         req.GET.get("cmp", ""),
            "show_search": show_search,
            "item_template": item_template,
            "post_url":    post_url,
            "headers":     headers,
            "message_log": paginated(req, combined_message_log(checked), prefix="msg", wrapper=__combined_message_log_row),
            "reporters":   paginated(req, model_class.objects.all(), wrapper=__decorate) })

    # if we just searched via GET (not via AJAX), store the hits
    # in a cookie for the client-side javascript to pick up. if
    # we don't, the javascript will overwrite the classes that
    # set in the template
    if filtered:
        flat_hits = " ".join(map(str, hits))
        resp.set_cookie("recip-hit", flat_hits)

        # update the search cookie (in the same weird-ass
        # pipe-delimited format as in the client-side script),
        # in case we're  mixing js and non-js searches
        resp.set_cookie("recip-search", 
            "|".join([
                req.GET["field"],
                req.GET["cmp"],
                req.GET["query"]]))

    return resp


def search(req):

    # fetch the data, filtering by ALL GET
    # parameters (raise if any are invalid)
    try:
        filters = dict([(str(k), v) for k, v in req.GET.items()])
        results = Reporter.objects.filter(**filters)

    except FieldError, e:
        return HttpResponse(e.message,
            status=500, mimetype="text/plain")

    recips = results.values_list("pk", flat=True)

    return HttpResponse(
        " ".join(map(str, recips)),
        content_type="text/plain")


def __redir_to_index():
    return HttpResponseRedirect(
        reverse("messaging-index"))


def all(req):
    """If this view is requested directly, add the primary key of every
       recipient to the recip-checked cookie (which is used to pass around
       the list of recipients that the user is planning to message), and
       redirect to the index to view it. If the view was requested by AJAX,
       return only the data that we _would_ have cookied, to allow the client
       to do it without reloading the page."""

    recips = Reporter.objects.values_list("pk", flat=True)

    if req.is_ajax():
        return HttpResponse(
            " ".join(map(str, recips)),
            content_type="text/plain")

    else:
        resp = __redir_to_index()
        flat_recips = "%20".join(map(str, recips))
        resp.set_cookie("recip-checked", flat_recips)
        return resp


def none(req):
    """Delete the reicp-checked cookie, and redirect back to
       the messaging index. This is another HTML-only fallback."""

    resp = __redir_to_index()
    resp.delete_cookie("recip-checked")
    return resp


def clear(req):
    """Delete the recip-error and recip-sent cookies, which are used
       to store the primary keys of recipients that receive (or fail to
       receive) messages, for users to inspect on the messaging index."""

    resp = __redir_to_index()
    resp.delete_cookie("recip-error")
    resp.delete_cookie("recip-sent")
    return resp





def _send_message(req, id, text):
    # also send the message, by hitting the ajax url of the messaging app
    data = {"uid": id, "text": text}
    encoded = urllib.urlencode(data)
    headers = {"Content-type": "application/x-www-form-urlencoded", 
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection(req.META["HTTP_HOST"])
    conn.request("POST", "/ajax/messaging/send_message", encoded, headers)
    response = conn.getresponse()
 
def parse_csv(filename=""):
    '''helper function to parse phone_number, message CSV files'''
    to_return = []
    with open(filename) as f:
        msglist = csv.reader(f)
        for row in msglist:
            obj = PersistantConnection.objects.get(identity=row[0])
            to_return.append({"id":obj.reporter, "number":obj.identity, "msg":row[1]})
    return to_return
 
@login_required
def confirm_csv_sms(request,template_name="confirm_csv.html"):
    '''Chance to view what SMS will be sent before sending'''
    context = {}
    
    if request.method == 'POST':
        try:
            if request.POST["confirmed"] == 1:
                # send them
                msglist = parse_csv(request.POST["temp-file"])
                for m in msglist:
                    _send_message(request, m["id"], m["msg"])
                return HttpResponseRedirect(reverse("reports.views.upload_csv_sms")
            else:
                # get them all
                msglist = parse_csv(request.FILES["csv_file_upload"], True)
                context['msglist'] = msglist
                tf = tempfile.NamedTemporaryFile(delete=False)
                with open(request.FILES["csv_file_upload"]) as f:
                    tf.write(f.read())
                context['temp-file'] = tf.name 
        except Exception, e:
            logging.error("Error importing csv file.", 
                          extra={'exception':e, 
                                 'request.POST': request.POST, 
                                 'request.FILES': request.FILES, 
                                 'form':form})
            context['errors'] = "Could not commit build: " + str(e)
    return render_to_response(request, template_name, context)
 
@login_required
def upload_csv_for_sms(request,template_name="upload_csv.html"):
    '''A view for bulk sending SMS from a CSV file upload'''
    context = {}
    
    if request.method == 'POST':
        try:
            msglist = parse_csv(request.FILES["csv_file_upload"])
        except Exception, e:
            logging.error("Error importing csv file.", 
                          extra={'exception':e, 
                                 'request.POST': request.POST, 
                                 'request.FILES': request.FILES, 
                                 'form':form})
            context['errors'] = "Could not commit build: " + str(e)
        return HttpResponseRedirect(reverse("reports.views.confirm_csv_sms")
    return render_to_response(request, template_name, context)

