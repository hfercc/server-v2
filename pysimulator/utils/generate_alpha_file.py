import os, sys
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-t', dest='type', default='normal')
    parser.add_option('-n',dest='alpha_name')
    (options, args) = parser.parse_args()
    
    if options.alpha_name == '':
        print 'alpha name can not be empty'
        sys.exit()
    
    template_f_name = ''
    if options.type == 'cached':
        template_f_name = 'utils/alpha_cached_template_trial.py'
    else:
        template_f_name = 'utils/alpha_template.py'

    template_f = open(template_f_name)
    target_f = open('./{0}.py'.format(options.alpha_name), 'w')

    for line in template_f:
        if 'alpha_template' in line:
            line = line.replace('alpha_template', options.alpha_name)
        target_f.write(line)

    template_f.close()
    target_f.close()
