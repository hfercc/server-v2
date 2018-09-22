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

from glob import glob
libs_dir = os.path.join(default_storage.path(MEDIA_ROOT),'libs')
base_dir = '/'.join(PROJECT_ROOT.split('/')[:-1])
def get_path(report):
    base_dir = '/'.join(PROJECT_ROOT.split('/')[:-1])
    return os.path.join(base_dir, report.file[1:])
def prepare(report):
    full_path = get_path(report.file)
    shutil.copy(get_dir(get_path(report.file), file_name = report.alpha_name + '.py'), os.path.join(base_dir, 'pysimulator'))
    shutil.copy(get_dir(get_path(report.file), file_name = 'config.xml'), os.path.join(base_dir, 'pysimulator'))

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
    print(full_path)
    try:
        f = zipfile.ZipFile(full_path, 'r')
        path_to = get_dir(full_path)
        for file in f.namelist():
            if file in ['config.xml','report.pdf', report.alpha_name + '.py']:
                print(os.path.join(path_to, file))
                if os.path.exists(os.path.join(path_to, file)):
                    os.remove(os.path.join(path_to, file))
                f.extract(file, path_to)
        f.close()
    except:
        pass

def validate_files(report):
    folder = get_dir((get_path(report)))
    for file in [report.alpha_name + '.py','config.xml','report.pdf']:
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
    print(env)
    env['PYTHONPATH']='/home/alpha-service/PySimulator-Research-1.0.0/lib:/home/alpha-service/PySimulator-Research-1.0.0/alpha' 
    prepare(report)
    os.chdir(os.path.join(base_dir, 'pysimulator'))
    pipe = subprocess.Popen('./compile.sh {}'.format(report.alpha_name + '.py') , shell=True, env=env)
    pipe.communicate()
    with open('config_compile.xml', 'w') as f:
        x = get('config.xml')
        x = generate(x)
        print(x)
        f.write(x)
    pipe = subprocess.Popen('python run.py -c config_compile.xml' , shell=True, env=env)
    pipe.communicate()
    if os.path.exists('output'):
        if os.path.exists(os.path.join(get_dir(get_path(report)), 'output')):
            shutil.rmtree(os.path.join(get_dir(get_path(report)), 'output'))
        shutil.copytree('output', os.path.join(get_dir(get_path(report)), 'output'))
        fileset =  FileRecord.objects.filter(Q(author=report.author) & Q(report=report))
        if (len(fileset) == 0):
            FileRecord.objects.create(path=os.path.join(get_dir(get_path(report)), 'output','output_pnl.png'), author=report.author, report=report, name='output_pnl.png')
            FileRecord.objects.create(path=os.path.join(get_dir(get_path(report)), 'output','output_ret.csv'), author=report.author, report=report, name='output_ret.csv')
            FileRecord.objects.create(path=os.path.join(get_dir(get_path(report)), 'output','output_performance.csv'), author=report.author, report=report,name='output_performance.csv')
        os.remove(os.path.join(base_dir, 'pysimulator', 'config.xml'))
        shutil.rmtree('build')
        os.remove('alpha/{}.so'.format(report.alpha_name))
        shutil.rmtree('output')
        return True
    else:
        return False



