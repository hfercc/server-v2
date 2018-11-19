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
def Query(pk):
    report = Report.objects.get(report_id=pk)
    print('jobs {} running....'.format(pk))
    report.status = 1
    report.save()
    flag = False
    utils.unzip(report)
    if (utils.validate_files(report)):
        try:
            flag,submitted_status = utils.compile_alpha(report)             
        except RuntimeError as e:
            report.error_message = u"编译错误"
        if (flag == True):
            if submitted_status == 1:
                report.status = 4
            else:
                report.status = 5
        else:
            report.status = 3
    else:
        report.error_message = u"解压错误或文件名错误"
        report.status = 3
    report.save()
    print('jobs[ts_id=%s] done' % report.report_id)
