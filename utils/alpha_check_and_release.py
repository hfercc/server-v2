## This script implements alpha criterion check:
## alpha_id unique check, correlation check, sharpe ratio check, turnover check, return check

import numpy as np
import os
import pymysql
from scipy.stats.stats import pearsonr
from optparse import OptionParser
from xml.etree.ElementTree import ElementTree,Element
import xml.etree.ElementTree as ET
import datetime
import sys
import glob

## check whether the given alpha_id exists in alpha_details table
#  @param alpha_id 
#  @return if exists return False, otherwise return True
def  check_unique_alphaid(alpha_id):
    conn = pymysql.connect(host='192.168.0.166',user='alpha-service',password='MXalpha@2018', db='alphas_info')
    cursor = conn.cursor()
    sql = "select `alpha_id` from `alpha_details`"
    reCount = cursor.execute(sql)
    res_tuple = cursor.fetchall()
    
    res = True
    for rec in res_tuple:
        if alpha_id == rec[0]:
            print 'Duplicate alpha_id'
            res = False
            break

    conn.close()
    return res

## check the highest correlation the given alpha return with alphas in database
# @param ret numpy array
# @param corr_limit the upper limit of correlation
# @return True if the highest correlation <= corr_limit otherwise False
def check_correlation(ret, corr_limit, sim_type, universe):
    all_return_dir = '/home/data/alpha/factor_return'
    ret_file_list = glob.glob(all_return_dir + '/*{0}_{1}*'.format(sim_type, universe))
    max_corr = -1
    max_corr_id = ''
    for ret_f in ret_file_list:
        #ret_f_path = os.path.join(all_return_dir, ret_f)
        ret_ary = np.fromfile(ret_f)

        min_len = min(len(ret),len(ret_ary))
        corr = pearsonr(ret[:min_len], ret_ary[:min_len])[0]
        if corr > max_corr:
            max_corr = corr
            max_corr_id = ret_f.split('/')[-1].split('.')[0]

    if max_corr > corr_limit:
        print '[FAILURE][alpha_id:{0},corr:{1}]'.format(max_corr_id, max_corr)

    return max_corr <= corr_limit

## check whether sharpe ratio satisfy given criterion
# @param year_sharpe sharpe of each year
# @param overall_sharpe overall sharpe
# @param year_sharpe_limit the lower limit of each year's sharpe
# @param overall_sharpe_limit the lower limit of overall sharpe
# @return True or False
def check_sharpe_ratio(year_sharpe, overall_sharpe, year_sharpe_limit, overall_sharpe_limit):
    year_sharpe_flag = np.sum(year_sharpe >= year_sharpe_limit) == len(year_sharpe)
    overall_sharpe_flag = overall_sharpe >= overall_sharpe_limit
    return year_sharpe_flag and overall_sharpe_flag

## check turnover and return criterion
# @param overall_tvr overall turnover
# @param overall_ret overall return
# @param cost_rate 
# @return True or False
def check_turnover_return(overall_tvr, overall_ret, cost_rate=0.0016):
    if overall_tvr <= 0.4:
        return True
    elif overall_tvr/2.0 * 250 * cost_rate * 0.8 <= overall_ret:
        return True
    else:
        return False
def read_from_path(performance_path, return_path):
    tvr_list = []
    ret_list = []
    sharpe_list = []

    ## read performance file
    perf_f = open(performance_path)
    i = 0
    for line in perf_f:
        i += 1
        if i == 1:
            continue
        line = line.strip('\n')
        tokens = line.split()
        if len(tokens) < 8:
            continue
        tvr_list.append(float(tokens[1])/100.0)
        ret_list.append(float(tokens[2])/100.0)
        sharpe_list.append(float(tokens[6]))

    daily_ret_list = []
    ## read daily return file
    daily_ret_f = open(return_path)
    i = 0
    for line in daily_ret_f:
        i += 1
        if i == 1:
            continue
        line = line.strip('\n')
        tokens = line.split(',')
        if len(tokens) < 2:
            continue
        daily_ret_list.append(float(tokens[1]))

    yearly_tvr = np.array(tvr_list[:-1])
    yearly_ret = np.array(ret_list[:-1])
    yearly_sharpe = np.array(sharpe_list[:-1])

    overall_tvr = tvr_list[-1]
    overall_ret = ret_list[-1]
    overall_sharpe = sharpe_list[-1]

    daily_ret_ary = np.array(daily_ret_list)

    return (yearly_tvr, yearly_ret, yearly_sharpe, overall_tvr, overall_ret, overall_sharpe, daily_ret_ary)

def check_criterion(daily_ret_ary, yearly_sharpe, overall_sharpe, overall_tvr, overall_ret, sim_type, universe):
    corr_flag = check_correlation(daily_ret_ary, 0.8, sim_type, universe)
    sharpe_flag = check_sharpe_ratio(yearly_sharpe, overall_sharpe, 0, 1.5)
    turnover_flag = check_turnover_return(overall_tvr, overall_ret, 0.0016)

    if corr_flag == False:
        print '[INFO]correlation check: Failed'

    if sharpe_flag == False:
        print '[INFO]sharpe check: Failed'

    if turnover_flag == False:
        print '[INFO]turnover check: Failed' 

    if corr_flag and sharpe_flag and turnover_flag:
        return True
    else:
        return False

def insert2db(alpha_id, s_type, universe, author, yearly_tvr, yearly_ret, yearly_sharpe):    
    if len(yearly_tvr) < 10:
        yearly_tvr = np.append(np.zeros(10-len(yearly_tvr)), yearly_tvr)
    if len(yearly_ret) < 10:
        yearly_ret = np.append(np.zeros(10-len(yearly_ret)), yearly_ret)
    if len(yearly_sharpe) < 10:
        yearly_sharpe = np.append(np.zeros(10-len(yearly_sharpe)), yearly_sharpe)

    try:
        conn = pymysql.connect(host='192.168.0.166',user='alpha-service',password='MXalpha@2018', db='alphas_info')
        cursor = conn.cursor()
        formatted_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO `alpha_details` (`alpha_id`, `author`, `type`, `universe`, `submission_date`, `turnover_0`, `turnover_1`, `turnover_2`, `turnover_3`, `turnover_4`, `turnover_5`, `turnover_6`, `turnover_7`, `turnover_8`, `turnover_9`, `return_0`, `return_1`, `return_2`, `return_3`, `return_4`, `return_5`, `return_6`, `return_7`, `return_8`, `return_9`, `sharpe_0`, `sharpe_1`, `sharpe_2`, `sharpe_3`, `sharpe_4`, `sharpe_5`, `sharpe_6`, `sharpe_7`, `sharpe_8`, `sharpe_9`, `updatetime`) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (alpha_id, author, s_type, universe, datetime.datetime.now().strftime('%Y%m%d'), float(yearly_tvr[-1]), float(yearly_tvr[-2]), float(yearly_tvr[-3]), float(yearly_tvr[-4]), float(yearly_tvr[-5]), float(yearly_tvr[-6]), float(yearly_tvr[-7]), float(yearly_tvr[-8]), float(yearly_tvr[-9]), float(yearly_tvr[-10]), float(yearly_ret[-1]), float(yearly_ret[-2]), float(yearly_ret[-3]), float(yearly_ret[-4]), float(yearly_ret[-5]), float(yearly_ret[-6]), float(yearly_ret[-7]), float(yearly_ret[-8]), float(yearly_ret[-9]), float(yearly_ret[-10]), float(yearly_sharpe[-1]), float(yearly_sharpe[-2]), float(yearly_sharpe[-3]), float(yearly_sharpe[-4]), float(yearly_sharpe[-5]), float(yearly_sharpe[-6]), float(yearly_sharpe[-7]), float(yearly_sharpe[-8]), float(yearly_sharpe[-9]), float(yearly_sharpe[-10]), formatted_date))
        conn.commit()
    finally:
        conn.close()

def copy_so_file_2lib(so_file_path):
    os.system("scp {0} alpha-service@192.168.0.169:/home/data/alpha/lib/".format(so_file_path))

# copy source file to 192.168.0.169:/home/alpha-service/source_file_tmp/ first
# then use cron job to add the new source file to git repository
def submit_source_file_2Git(source_file_path):
    os.system("scp {0} alpha-service@192.168.0.169:/home/alpha-service/source_file_tmp/".format(source_file_path))


def read_xml(in_path):
    tree = ElementTree()
    tree.parse(in_path)
    return tree

def copy_config_file_2configs(original_config_path, alpha_id, formula_flag):
    ## read original_config_path
    ## modify items in the original_config_path, for example, enddate in <SimulationSetting>, path in <Alpha>, output_name and save_dir in <Performance>..
    ## save the modified config and then copy it to /home/data/alpha/configs
    xml_f = open(original_config_path, 'r')
    xml_string = xml_f.read()
    xml_string = xml_string.replace('/home/data/research_cache', '/home/data/cache')
    xml_f.close()
    root = ET.fromstring(xml_string)

    # set 'enddate' to today
    simset_node = root.find('SimulationSetting')
    simset_node.set('enddate', datetime.datetime.now().strftime('%Y%m%d'))    
    simset_node.set('enable_dumper', 'true')

    # add dumper node to root
    dumper_node = Element('AlphaDumper')
    dumper_node.set('id', 'AlphaDumper')
    dumper_node.set('path', 'binary_dumper.so')
    dumper_node.set('output_dir', '/home/data/alpha/factor_value/{0}'.format(alpha_id))
    root.append(dumper_node)

    # set 'path' in Alpha
    alpha_node = root.find('Alpha')
    if formula_flag == 'false':
        alpha_node.set('path', '/home/data/alpha/lib/alpha_{0}.so'.format(alpha_id))
    else:
        alpha_node.set('path', 'alpha_formulaic_filterout_zombie.so')

    # set 'output_name', 'save_dir', 'ret_dump_dir' in Performance
    perf_node = root.find('Performance')
    perf_node.set('output_name', alpha_id)
    perf_node.set('save_dir', '/home/data/alpha/factor_performance/{0}'.format(alpha_id))
    perf_node.set('ret_dump_dir', '/home/data/alpha/factor_return')

    # write to temprary file
    tree = ET.ElementTree(element=root)
    tree.write('{0}.xml'.format(alpha_id))
    # copy to /home/data/alpha/configs and delete temprary file
    os.system("scp {0}.xml alpha-service@192.168.0.169:/home/alpha-service/production_configs/ && rm -f {1}.xml".format(alpha_id, alpha_id))

if __name__ == '__main__':
    ## python alpha_check_and_release.py --alpha_id WQ083_IC_hedge_zz500 --type IC_hedge --universe zz500 --author xingk --performance_file alpha_submission_test/WQ083_IC_hedge_performance.csv --daily_return_file alpha_submission_test/WQ083_IC_hedge_ret.csv --source_file_path alpha_submission_test/alpha_WQ083_IC_hedge_zz500.py --so_file_path alpha_submission_test/alpha_WQ083_IC_hedge_zz500.so --config_path alpha_submission_test/WQ083_IC_hedge.xml
    #
    parser = OptionParser()
    parser.add_option('--alpha_id', dest="alpha_id")
    parser.add_option('--type', dest="type")
    parser.add_option('--universe', dest="universe")
    parser.add_option('--author', dest="author")
    parser.add_option('--performance_file', dest='performance_file') # e.g, WQ083_IC_hedge_performance.csv
    parser.add_option('--daily_return_file', dest='daily_return_file') # e.g. WQ083_IC_hedge_ret.csv
    parser.add_option('--source_file_path', dest="source_file_path",default="") # e.g. alpha_WQ083_IC_hedge_zz500.py
    parser.add_option('--so_file_path', dest="so_file_path",default="") # e.g. alpha_WQ083_IC_hedge_zz500.so
    parser.add_option('--config_path', dest="config_path") # e.g. WQ083_IC_hedge_zz500.xml
    parser.add_option('--formula', dest="formula", default="false")
    (options, args) = parser.parse_args()

    # if alpha_id is duplicate with existing alphas, return
    print '[INFO]check alpha_id uniqueness...'
    if check_unique_alphaid(options.alpha_id) == False:
        print '[INFO]check alpha_id uniqueness: Failed'
        sys.exit(0)
    print '[INFO]check alpha_id uniqueness: OK'

    (yearly_tvr, yearly_ret, yearly_sharpe, overall_tvr, overall_ret, overall_sharpe, daily_ret_ary) = read_from_path(options.performance_file, options.daily_return_file)
    # if the performance satisfy given criterion, insert this alpha into database
    print '[INFO]check criterion...'
    if check_criterion(daily_ret_ary, yearly_sharpe, overall_sharpe, overall_tvr, overall_ret, options.type, options.universe):
        print '[INFO]check criterion: OK'

        # insert this alpha into table alpha_details        
        print '[INFO]insert into DB...'
        insert2db(options.alpha_id, options.type, options.universe, options.author, yearly_tvr, yearly_ret, yearly_sharpe)
        print '[INFO]insert into DB: OK'

        # copy .so file to /home/data/alpha/lib
        if options.formula != "true":
            print '[INFO]copy .so to /home/data/alpha/lib...'
            copy_so_file_2lib(options.so_file_path)
            print '[INFO]copy .so to /home/data/alpha/lib: OK'

            print '[INFO]copy source file to /home/alpha-service/source_file_tmp...'
            submit_source_file_2Git(options.source_file_path)
            print '[INFO]copy source file to /home/alpha-service/source_file_tmp: OK'

        # copy config file to /home/data/alpha/configs
        print '[INFO]copy config to /home/alpha-service/production_configs...'
        copy_config_file_2configs(options.config_path, options.alpha_id, options.formula)
        print '[INFO]copy config to /home/alpha-service/production_configs: OK'
