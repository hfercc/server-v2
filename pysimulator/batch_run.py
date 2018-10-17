from optparse import OptionParser
import subprocess
import os

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--config',dest='config')
    (options, args) = parser.parse_args()
    
    configs = os.listdir(options.config)
    for cfg in configs:
        print 'run {0}'.format(cfg)
        exec_cmd = ['python', 'run.py', '-c', os.path.join(options.config, cfg)]
        subprocess.Popen(exec_cmd)
