# -*- encoding: utf-8 -*-
import re
import tempfile
import os.path
import functools
import mimetypes
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File as FileWrapper
from django.db.models import Q
import zipfile
from backtest_py2.settings import MEDIA_ROOT, BASE_DIR, PROJECT_ROOT
import shutil
import subprocess
from .xmlparse import get, generate
import json
from file.models import FileRecord
from alpha_check_and_release import *

from glob import glob
libs_dir = os.path.join(default_storage.path(MEDIA_ROOT),'libs')
base_dir = '/'.join(PROJECT_ROOT.split('/')[:-1])
def get_path(report):
    base_dir = '/'.join(PROJECT_ROOT.split('/')[:-1])
    return os.path.join(base_dir, report.file[1:])
def prepare(report):
    full_path = get_path(report)
    shutil.copy(get_dir(get_path(report), file_name = report.alpha_name + '.py'), os.path.join(base_dir, 'pysimulator'))
    if 
    shutil.copy(get_dir(get_path(report), file_name = 'config.xml'), os.path.join(base_dir, 'pysimulator'))

def get_dir(path , file_name = None):
    if file_name == None:
        return os.path.dirname(path)
    else:
        return os.path.join(os.path.dirname(path), file_name)

def store_file(fd, user, alpha_name):
    """
    Given a file-like object and stores it with default storage system.

    Returns a tuple (file_name, mime_type), where the file name is relative to
    MEDIA_ROOT.
    """
    full_path = default_storage.path(os.path.join(user.username, alpha_name, os.path.basename(fd.name)))
    if (os.path.exists(full_path)):
        os.remove(full_path)
    name = default_storage.save(os.path.join(user.username, alpha_name, os.path.basename(fd.name)), fd)

    return name, mimetypes.guess_type(name)[0] or ''

def unzip(report):
    full_path = get_path(report)
    try:
        f = zipfile.ZipFile(full_path, 'r')
        path_to = get_dir(full_path)
        for file in f.namelist():
            print(file)
            if file in ['config.xml', 'alpha.py']:

                if os.path.exists(os.path.join(path_to, file)):
                    print('overwrite')
                    os.remove(os.path.join(path_to, file))
                f.extract(file, path_to)
        os.rename(os.path.join(path_to, 'alpha.py'), os.path.join(path_to, report.alpha_name + '.py'))
        f.close()
    except:
        pass

def validate_files(report):
    folder = get_dir((get_path(report)))
    if report.alpha_type==0:
        for file in [report.alpha_name + '.py','config.xml']:
            if not os.path.exists(os.path.join(folder, file)):
                return False
        return True
    else:
        for file in ['config.xml','report.pdf']:
            if not os.path.exists(os.path.join(folder, file)):
                return False
        return True

def compile_alpha(report):
    '''
    from .setup import _compile_alpha
    work_path = os.path.join(base_dir, 'temp_' + report.author.username)
    if not os.path.exists(work_path):
        os.mkdir(work_path)
    full_path = get_dir(get_path(report))
    os.chdir(work_path)
    print(os.path.join(full_path, report.alpha_name + '.py'))
    _compile_alpha(os.path.join(full_path, report.alpha_name + '.py'))
    file_to_move = glob(os.path.join(work_path,'build/lib*/*.so'))
    if (len(file_to_move) > 0):
        if os.path.exists(os.path.join(full_path,'alpha')):
            shutil.rmtree(os.path.join(full_path,'alpha'))
        os.mkdir(os.path.join(full_path,'alpha'))
        shutil.move(file_to_move[0], os.path.join(full_path,'alpha/'))
        os.chdir(full_path)
        shutil.rmtree(work_path)
        return True
    else:
        return False
    '''
    env=os.environ.copy()
    env['PYTHONPATH']='/home/data/Simulator/MXSimulator-Research-1.0.0/lib/core:/home/data/Simulator/MXSimulator-Research-1.0.0/lib/loader:/home/data/Simulator/MXSimulator-Research-1.0.0/alpha' 
    prepare(report)
    os.chdir(os.path.join(base_dir, 'pysimulator'))
    if report.alpha_type == 0:
        pipe = subprocess.Popen('./compile.sh {}'.format(report.alpha_name + '.py') , shell=True, env=env)
        pipe.communicate()
    with open('config_compile.xml', 'w') as f:
        x = get('config.xml')
        x = generate(x, report)
        print(x)
        f.write(x)
    pipe = subprocess.Popen('python run.py -c config_compile.xml' , shell=True, env=env)
    pipe.communicate()
    if os.path.exists('output'):
        fileset =  FileRecord.objects.filter(Q(author=report.author) & Q(report=report))
        print(len(fileset))
        if (len(fileset) == 0):
            FileRecord.objects.create(content=open(os.path.join('output','output_pnl.png'), 'rb').read(), author=report.author, report=report, name='output_pnl.png')
            FileRecord.objects.create(content=open(os.path.join('output','output_ret.csv'), 'rb').read(), author=report.author, report=report, name='output_ret.csv')
            FileRecord.objects.create(content=open(os.path.join('output','output_performance.csv'), 'rb').read(), author=report.author, report=report,name='output_performance.csv')
        else:
            for f in fileset:
                if f.name == 'output_pnl.png':
                    f.content = open(os.path.join('output','output_pnl.png'), 'rb').read()
                elif f.name == 'output_ret.csv':
                    f.content = open(os.path.join('output','output_ret.csv'), 'rb').read()
                else:
                    f.content = open(os.path.join('output','output_performance.csv'), 'rb').read()
                f.save(update_fields=['content'])
        (yearly_tvr, yearly_ret, yearly_sharpe, overall_tvr, overall_ret, overall_sharpe, daily_ret_ary) = read_from_path('output/output_performance.csv', 'output/output_ret.csv')
        print '[INFO]check alpha_id uniqueness...'
        if check_unique_alphaid(report.alpha_name) == False:
            print '[INFO]check alpha_id uniqueness: Failed'
        else:
            print '[INFO]check alpha_id uniqueness: OK'
            print '[INFO]check criterion...'
            if check_criterion(daily_ret_ary, yearly_sharpe, overall_sharpe, overall_tvr, overall_ret):
                print '[INFO]check criterion: OK'

                # insert this alpha into table alpha_details        
                print '[INFO]insert into DB...'
                insert2db(report.alpha_name, report.type, report.universe, report.author, yearly_tvr, yearly_ret, yearly_sharpe)
                print '[INFO]insert into DB: OK'

                # copy .so file to /opt/data/alpha/lib
                if report.alpha_type == 0:
                    print '[INFO]copy .so to /home/data/alpha/lib...'
                    copy_so_file_2lib(os.path.join('build',report.alpha_name + '.py'))
                    print '[INFO]copy .so to /home/data/alpha/lib: OK'

                    print '[INFO]copy source file to /home/alpha-service/source_file_tmp...'
                    A.submit_source_file_2Git(report.alpha_name + '.py')
                    print '[INFO]copy source file to /home/alpha-service/source_file_tmp: OK'

                # copy config file to /opt/data/alpha/configs
                print '[INFO]copy config to /home/data/alpha/configs...'
                copy_config_file_2configs('config_compile.xml', report.alpha_name)
                print '[INFO]copy config to /home/data/alpha/configs: OK'
        os.remove(os.path.join(base_dir, 'pysimulator', 'config.xml'))
        os.remove(os.path.join(base_dir, 'pysimulator', report.alpha_name + '.py'))
        shutil.rmtree('build')
        os.remove('alpha/{}.so'.format(report.alpha_name))
        shutil.rmtree('output')
        return True
    else:
        return False



