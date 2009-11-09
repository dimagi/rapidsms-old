from rapidsms.webui.utils import render_to_response, paginated
from models import *
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, permission_required


@login_required
@permission_required("logger.can_view")
def index(req):
    template_name="logger/index_flat.html"
    columns = (("date", "Date"),
               ("connection__identity", "From/To"), 
               ("connection__backend", "Backend"), 
               ("text", "Message"),
               ("is_incoming", "Direction"))
    sort_column, sort_descending = _get_sort_info(req, default_sort_column="date", 
                                                  default_sort_descending=True)
    sort_desc_string = "-" if sort_descending else ""
    
    all = Message.objects.all().order_by("%s%s" % (sort_desc_string, sort_column))
    messages = paginated(req, all)
    return render_to_response(req, template_name, {"columns": columns,
                                                   "messages": messages,
                                                   "sort_column": sort_column,
                                                   "sort_descending": sort_descending})

def _get_sort_info(request, default_sort_column, default_sort_descending):
    sort_column = default_sort_column
    sort_descending = default_sort_descending
    if "sort_column" in request.GET:
        sort_column = request.GET["sort_column"]
    if "sort_descending" in request.GET:
        if request.GET["sort_descending"].startswith("f"):
            sort_descending = False
        else:
            sort_descending = True
    return (sort_column, sort_descending)

def _old_index(req):
    # Reference to the old view of the old tables.
    # Ordinarily I would delete this, but this log is still 
    # around in several deployments
    template_name="logger/index.html"
    incoming = IncomingMessage.objects.order_by('received')
    outgoing = OutgoingMessage.objects.order_by('sent')
    all = []
    [ all.append(msg) for msg in incoming ]
    [ all.append(msg) for msg in outgoing]
    # sort by date, descending
    all.sort(lambda x, y: cmp(y.date, x.date))
    return render_to_response(req, template_name, { "messages": all })
