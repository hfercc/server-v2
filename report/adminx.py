import xadmin
from .models import Report

class ReportAdmin(object):
    list_display=["alpha_name", "report_id", "file", "status"]
    search_fields=["alpha_name", ]

xadmin.site.register(Report, ReportAdmin)