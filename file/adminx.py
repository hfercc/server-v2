import xadmin
from .models import FileRecord

class FileRecordAdmin(object):
    list_display=["report","author","file_id","path"]
    search_fields=["report", ]

xadmin.site.register(FileRecord, FileRecordAdmin)