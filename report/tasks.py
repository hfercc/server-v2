# -*- encoding: utf-8 -*-
import time
from celery import task
from .models import Report
from backtest_py2.settings import MEDIA_ROOT
from django.core.files.storage import default_storage
from utils import utils
import os
import fcntl

@task
def Query(ts_id):
    print('jobs[ts_id=%s] running....' % ts_id)
    queryset = Report.objects.filter(status = 0)
    inprocess_queryset = Report.objects.filter(status = 1)
    in_length = len(inprocess_queryset)
    for report in queryset:
        if(in_length < 5):
            report.status = 1
            report.save()
            print(report.alpha_name, report.file)
            in_length += 1
            flag = False
            utils.unzip(report)
            if (utils.validate_files(report)):
                try:
                    flag = utils.compile_alpha(report)             
                except RuntimeError as e:
                    report.error_message = u"编译错误"
            #utils.clean()
                if (flag == True):
                    report.status = 2
                else:
                    report.status = 3
            else:
                report.error_message = u"解压错误或文件名错误"
                report.status = 3
            report.save()
    print('jobs[ts_id=%s] done' % ts_id)
