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
from django.contrib.auth import get_user_model
from glob import glob
User = get_user_model()

from glob import glob
libs_dir = os.path.join(default_storage.path(MEDIA_ROOT),'libs')
base_dir = '/'.join(PROJECT_ROOT.split('/')[:-1])
def get_path(report):
    base_dir = '/'.join(PROJECT_ROOT.split('/')[:-1])
    return os.path.join(base_dir, report.file[1:])
def prepare(report):
    full_path = get_path(report)
    if report.alpha_type == 0:
        if os.path.exists(os.path.join(base_dir, 'pysimulator', report.alpha_name + '.py')):
            print('Found source file in pysimulator. Removing it.')
            os.remove(os.path.join(base_dir, 'pysimulator', report.alpha_name + '.py'))
        shutil.move(get_dir(get_path(report), file_name = report.alpha_name + '.py'), os.path.join(base_dir, 'pysimulator'))
    if os.path.exists(os.path.join(base_dir, 'pysimulator', 'config.xml')):
        print('Found config.xml in pysimulator. Removing it.')
        os.remove(os.path.join(base_dir, 'pysimulator', 'config.xml'))
    shutil.move(get_dir(get_path(report), file_name = 'config.xml'), os.path.join(base_dir, 'pysimulator'))

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
            if (file == 'alpha.py') or ('.xml' in file):
                if os.path.exists(os.path.join(path_to, file)):
                    print('Removed {}'.format(file))
                    os.remove(os.path.join(path_to, file))
                print('Overwrite {}'.format(file))
                f.extract(file, path_to)
        xml_file = glob(os.path.join(path_to, '*.xml'))[0]
        if os.path.exists(os.path.join(path_to,'config.xml')) and xml_file.split('/')[-1] != 'config.xml':
            os.remove(os.path.join(path_to,'config.xml'))
            print('Removed original config.xml')
            os.rename(xml_file, os.path.join(path_to,'config.xml'))
            print('Updated new config.xml')
        else:
            os.rename(xml_file, os.path.join(path_to,'config.xml'))
            print('Updated new config.xml')
        if os.path.exists(os.path.join(path_to, report.alpha_name + '.py')):
            os.remove(os.path.join(path_to, report.alpha_name + '.py'))
            print('Removed original source file')
        os.rename(os.path.join(path_to, 'alpha.py'), os.path.join(path_to, report.alpha_name + '.py'))
        print('Renamed new source file')
        f.close()
    except:
        pass

def validate_files(report):
    folder = get_dir((get_path(report)))
    if report.alpha_type==0:
        for file in [report.alpha_name + '.py','config.xml']:
            if not os.path.exists(os.path.join(folder, file)):
                print('Error: {} not existed'.format(file))
                return False
            print('Validated {}'.format(file))
        return True
    else:
        for file in ['config.xml']:
            if not os.path.exists(os.path.join(folder, file)):
                print('Error: {} not existed'.format(file))
                return False
            print('Validated {}'.format(file))
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
    print("Alpha name: {}".format(report.alpha_name))
    print("Alpha type: {}".format(report.alpha_type))
    universe_ = ['ALL', 'zz500', 'hs300', 'zz500T']
    type_     = ['longshort', 'longonly', 'IC_hedge', 'IF_hedge']
    env=os.environ.copy()
    env['PYTHONPATH']='/home/data/Simulator/MXSimulator-Research/lib/core:/home/data/Simulator/MXSimulator-Research/lib/loader:/home/alpha-service/server-v2/pysimulator/alpha' 
    prepare(report)
    print('Begin to compile source file')
    os.chdir(os.path.join(base_dir, 'pysimulator'))
    if report.alpha_type == 0:
        pipe = subprocess.Popen('./compile.sh {}'.format(report.alpha_name + '.py') , shell=True, env=env)
        pipe.communicate()
    with open('config_compile.xml', 'w') as f:
        print('Generating config_compile.xml')
        r, p = get('config.xml', report)
        x = generate(r, p, report)
        print(x)
        f.write(x)
    print('Generated config_compile.xml')
    pipe = subprocess.Popen('python run.py -c config_compile.xml' , shell=True, env=env)
    pipe.communicate()
    if os.path.exists('output'):
        print('Backtest succeeded.')
        fileset =  FileRecord.objects.filter(Q(author=report.author) & Q(report=report))
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
        (yearly_tvr, yearly_ret, yearly_sharpe, overall_tvr, overall_ret, overall_sharpe, daily_ret_ary, startdate) = read_from_path('output/output_performance.csv', 'output/output_ret.csv')
        print '[INFO]check alpha_id uniqueness...'
        if False:
            print '[INFO]check alpha_id uniqueness: Failed'
            report.error_message = 'check alpha_id uniqueness: Failed'
        else:
            print '[INFO]check alpha_id uniqueness: OK'
            print '[INFO]check criterion...'
            flag, err = check_criterion(daily_ret_ary, yearly_sharpe, overall_sharpe, overall_tvr, overall_ret, type_[report.type_code], universe_[report.universe], report.alpha_name)
            if flag:
                print '[INFO]check criterion: OK'

                # insert this alpha into table alpha_details        
                print '[INFO]insert into DB...'
                insert2db(report.alpha_name, type_[report.type_code], universe_[report.universe], report.author.username, yearly_tvr, yearly_ret, yearly_sharpe)
                print '[INFO]insert into DB: OK'
                
                print '[INFO]insert return into MongoDB...'
                update_correlation(report.alpha_name, type_[report.type_code], universe_[report.universe], daily_ret_ary, startdate)
                print '[INFO]insert return into MongoDB: OK'
                
                # copy .so file to /opt/data/alpha/lib
                if report.alpha_type == 0:
                    print '[INFO]copy .so to /home/data/alpha/lib...'
                    copy_so_file_2lib(os.path.join('alpha',report.alpha_name + '.so'))
                    print '[INFO]copy .so to /home/data/alpha/lib: OK'

                    print '[INFO]copy source file to /home/alpha-service/source_file_tmp...'
                    submit_source_file_2Git(report.alpha_name + '.py')
                    print '[INFO]copy source file to /home/alpha-service/source_file_tmp: OK'

                # copy config file to /opt/data/alpha/configs
                print '[INFO]copy config to /home/alpha-service/production_configs...'
                copy_config_file_2configs('config_compile.xml', report.alpha_name, report.alpha_type == 1)
                print '[INFO]copy config to /home/alpha-service/production_configs: OK'
                report.error_message = ''
            else:
                report.error_message = err
        os.remove(os.path.join(base_dir, 'pysimulator', 'config.xml'))
        if report.alpha_type == 0:
            os.remove(os.path.join(base_dir, 'pysimulator', report.alpha_name + '.py'))
            os.remove(os.path.join(base_dir, 'pysimulator', report.alpha_name + '.pyc'))
            shutil.rmtree('build')
            os.remove('alpha/{}.so'.format(report.alpha_name))
        shutil.rmtree('output')
        if len(report.error_message) == 0:
            return True, 1
        else:
            return True, 0
    else:
        print('Backtest failed. Cleaning files')
        os.remove(os.path.join(base_dir, 'pysimulator', 'config.xml'))
        if report.alpha_type == 0:
            os.remove(os.path.join(base_dir, 'pysimulator', report.alpha_name + '.py'))
        return False, 0



