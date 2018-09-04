from optparse import OptionParser
import subprocess
import os

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--folder',dest='folder')
    (options, args) = parser.parse_args()
    
    sub_folders = os.listdir(options.folder)
    for flder in sub_folders:
        print 'processing {0}'.format(flder)
        exec_cmd = ['python', 'generate_report.py', '--folder', os.path.join(options.folder, flder)]
        subprocess.Popen(exec_cmd)