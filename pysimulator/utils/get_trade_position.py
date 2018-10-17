import os
import numpy as np
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', dest='position_file')
    parser.add_option('-n',dest='number', default='-1')
    parser.add_option('-o', dest='output', default='trade_position.csv')
    (options, args) = parser.parse_args()

    number = int(options.number)
    position_f = open(options.position_file)
    tickers = []
    dates = []
    position_chg_list = []

    last_ary = None
    cur_ary = None

    lc = 0
    for line in position_f:
        lc += 1
        if lc == 1:
            line = line.strip('\n')
            tokens = line.split(',')
            if len(tokens) == 0:
                continue
            dates.append(tokens[0])
            pos_list = []
            for i in range(1, len(tokens)):
                tokens[i] = tokens[i].lstrip('[').rstrip(']')
                fields = tokens[i].split(':')
                tickers.append(fields[0])
                pos_list.append(float(fields[1]))

            last_ary = np.array(pos_list)

        else:
            line = line.strip('\n')
            tokens = line.split(',')
            if len(tokens) == 0:
                continue
            dates.append(tokens[0])
            pos_list = []
            for i in range(1, len(tokens)):
                tokens[i] = tokens[i].lstrip('[').rstrip(']')
                fields = tokens[i].split(':')
		if len(fields) < 2:
		    print lc
		    print line
                pos_list.append(float(fields[1]))
            cur_ary = np.array(pos_list)
            pos_chg = cur_ary - last_ary
	    last_ary = cur_ary
            chg_list = []
            for i in range(len(tickers)):
                chg_list.append((tickers[i], pos_chg[i]))

            chg_list.sort(reverse=True, key=lambda x:abs(x[1]))
            position_chg_list.append(chg_list)

    position_f.close()

    pos_chg_f = open(options.output, 'w')
    for i in range(len(position_chg_list)):
        line_str = '{0}'.format(dates[i])
        for j in range(len(position_chg_list[i])):
            if number < 0 or j < number:
                line_str += ',[{0}:{1}]'.format(position_chg_list[i][j][0], position_chg_list[i][j][1])
        line_str += '\n'
        pos_chg_f.write(line_str)
    pos_chg_f.close()
