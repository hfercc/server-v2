import numpy as np
from alpha_cached import alpha_cached
import formula_trans as tran
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression


def create():
    return example()


class example(alpha_cached):
    """description of class"""

    def __init__(self, *args, **kwargs):
        super(example, self).__init__(*args, **kwargs)
        self.basicfields = ['open', 'close', 'low', 'high', 'volume', 'amount', 'vwap', 'ret']
        self.finalname=""

    ## write your code below

    def initialize(self):
        super(example, self).initialize()
        self.init_str = tran.get_init_alpha(self.formula)
        tmp_str = tran.get_gene_alpha(self.formula)
        tmp_str = tmp_str.strip("'")
        self.gene_str = "self.finalname={0}".format(tmp_str)
        ## write your code below

    def on_start(self, data, start_di):
        super(example, self).on_start(data, start_di)
        for field in self.basicfields:
            self.indata[field] = []
        if self.benchmark is not None:
            self.indata['benchmarkopen']=[]
            self.indata['benchmarkclose']=[]
        for i in range(start_di):
            for field in self.basicfields:
                self.indata[field].append(data['essentials'][field][i - self.delay, :])
            if self.benchmark is not None:
                self.indata['benchmarkopen'].append(data[self.benchmark][i-self.delay,0])
                self.indata['benchmarkclose'].append(data[self.benchmark][i-self.delay,3])
            exec(self.init_str)

    #######################################functions#################################################
    def doinit(self, keyname, inkey, n=0):
        # return bool value: if this func performed action
        if inkey not in self.indata.keys():
            self.indata[inkey] = []
        if (len(self.indata[keyname]) <= n) or ((self.indata[keyname][-(n + 1)]) is None):
            self.indata[inkey].append(None)
            return True
        else:
            return False

    def scale(self, keyname, isinit=False):
        inkey = "scale(" + keyname + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            a = self.indata[keyname][-1]  # 1-d array
            self.indata[inkey].append(a / np.nansum(abs(a)))
        else:
            pass
        return inkey

    def delta(self, keyname, n, isinit=False):
        s = 'delta(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n) == False:
            self.indata[s].append(self.indata[keyname][-1] - self.indata[keyname][-(n + 1)])
        else:
            pass
        return s

    def log(self, keyname, isinit=False):
        # return nan when input number is negative
        inkey = "log(" + keyname + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            self.indata[inkey].append(np.log(self.indata[keyname][-1]))
        else:
            pass
        return inkey

    def cov(self,keynamex,keynamey,n,isinit=False):
        #self.delay should be no less than 1
        inkey= "cov(" + keynamex + "," + keynamey + "," + str(n) + ")"
        n= int(round(n))
        flag= self.doinit(keynamex,inkey,n-1)+self.doinit(keynamey,inkey,n-1)
        if isinit==False:
            del self.indata[inkey][0]
            in_x= np.array(self.indata[keynamex][-n::])
            in_y= np.array(self.indata[keynamey][-n::])
            in_len= len(self.indata[keynamex][-1])
            r= np.array([np.cov(in_x[:,i],in_y[:,i])[0,1] for i in range(in_len)])
            self.indata[inkey].append(r)
        elif flag==1:
            self.indata[inkey].append(None)
        elif flag==0:
            in_x= np.array(self.indata[keynamex][-n::])
            in_y= np.array(self.indata[keynamey][-n::])
            in_len= len(self.indata[keynamex][-1])
            r= np.array([(np.cov(in_x[:,i],in_y[:,i])[0,1]) for i in range(in_len)])
            self.indata[inkey].append(r)
        else:
            pass
        return inkey

    def corr(self, keynamex, keynamey, n, isinit=False):
        # self.delay should be no less than 1
        inkey = "corr(" + keynamex + "," + keynamey + "," + str(n) + ")"
        n = int(round(n))
        flag = self.doinit(keynamex, inkey, n - 1) + self.doinit(keynamey, inkey, n - 1)
        if isinit == False:
            del self.indata[inkey][0]
            in_x = np.array(self.indata[keynamex][-n::])
            in_y = np.array(self.indata[keynamey][-n::])
            in_len = len(self.indata[keynamex][-1])
            r = np.array([(pearsonr(in_x[:, i], in_y[:, i])[0]) for i in range(in_len)])
            self.indata[inkey].append(r)
        elif flag == 1:
            self.indata[inkey].append(None)
        elif flag == 0:
            in_x = np.array(self.indata[keynamex][-n::])
            in_y = np.array(self.indata[keynamey][-n::])
            in_len = len(self.indata[keynamex][-1])
            r = np.array([(pearsonr(in_x[:, i], in_y[:, i])[0]) for i in range(in_len)])
            self.indata[inkey].append(r)
        else:
            pass
        return inkey

    def exp(self, keyname, isinit=False):
        # return nan when input number is negative
        inkey = "exp(" + keyname + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            self.indata[inkey].append(np.exp(self.indata[keyname][-1]))
        else:
            pass
        return inkey

    def abs(self, keyname, isinit=False):
        # return nan when input number is negative
        inkey = "abs(" + keyname + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            self.indata[inkey].append(np.abs(self.indata[keyname][-1]))
        else:
            pass
        return inkey

    def sign(self, keyname, isinit=False):
        # return nan when input number is negative
        inkey = "sign(" + keyname + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            self.indata[inkey].append(np.sign(self.indata[keyname][-1]))
        else:
            pass
        return inkey

    def ceiling(self, keyname, isinit=False):
        # return nan when input number is negative
        inkey = "ceiling(" + keyname + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            self.indata[inkey].append(np.ceil(self.indata[keyname][-1]))
        else:
            pass
        return inkey

    def floor(self, keyname, isinit=False):
        # return nan when input number is negative
        inkey = "floor(" + keyname + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            self.indata[inkey].append(np.floor(self.indata[keyname][-1]))
        else:
            pass
        return inkey

    def rank(self, keyname, isinit=False):
        # return value is scale to [0,1] closed interval
        # same value will be ranked in order of appearance,nan will be converted to nan
        inkey = 'rank' + '(' + keyname + ')'
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            a = self.indata[keyname][-1]
            ceil = len(a) - np.isnan(a).sum()
            temp = a.argsort().argsort() + 1
            temp = np.where(temp > ceil, np.nan, temp)
            self.indata[inkey].append(temp)
        else:
            pass
        return inkey

    def plus(self, keynamex, keynamey, isinit=False):
        inkey = 'plus' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] + self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] + keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex + self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex + keynamey)

    def subtract(self, keynamex, keynamey, isinit=False):
        inkey = 'subtract' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] - self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] - keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex - self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex - keynamey)

    def multiply(self, keynamex, keynamey, isinit=False):
        inkey = 'multiply' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] * self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] * keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex * self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex * keynamey)

    def divide(self, keynamex, keynamey, isinit=False):
        inkey = 'divide' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        # return inf if divisor is 0
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] / self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] / keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex / self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex / keynamey)

    def negative(self, keyname, isinit=False):
        # return nan when input number is negative
        inkey = "negative(" + keyname + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinit == False or self.doinit(keyname, inkey) == False:
            self.indata[inkey].append(-1 * self.indata[keyname][-1])
        else:
            pass
        return inkey

    def power(self, keynamex, keynamey, isinit=False):
        inkey = 'power' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] ** self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] ** keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex ** self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex ** keynamey)

    def signedpower(self, keynamex, keynamey, isinit=False):
        inkey = 'signedpower' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(
                    np.sign(self.indata[keynamex][-1]) * np.abs(self.indata[keynamex][-1]) ** self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(
                    np.sign(self.indata[keynamex][-1]) * np.abs(self.indata[keynamex][-1]) ** keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(np.sign(keynamex) * np.abs(keynamex) ** self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (np.sign(keynamex) * np.abs(keynamex) ** keynamey)

    def delay(self, keyname, n, isinit=False):
        s = 'delay(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n) == False:
            self.indata[s].append(self.indata[keyname][-(n + 1)])
        else:
            pass
        return s

    def sum(self, keyname, n, isinit=False):
        s = 'sum(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            self.indata[s].append(np.sum(np.array(self.indata[keyname][-n::]), axis=0))
        else:
            pass
        return s

    def mean(self, keyname, n, isinit=False):
        s = 'mean(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            self.indata[s].append(np.mean(np.array(self.indata[keyname][-n::]), axis=0))
        else:
            pass
        return s

    def prod(self, keyname, n, isinit=False):
        s = 'prod(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            self.indata[s].append(np.prod(np.array(self.indata[keyname][-n::]), axis=0))
        else:
            pass
        return s

    def std(self, keyname, n, isinit=False):
        s = 'std(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            self.indata[s].append(np.std(np.array(self.indata[keyname][-n::]), axis=0))
        else:
            pass
        return s

    def tsmax(self, keyname, n, isinit=False):
        s = 'tsmax(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            self.indata[s].append(np.max(np.array(self.indata[keyname][-n::]), axis=0))
        else:
            pass
        return s

    def tsmin(self, keyname, n, isinit=False):
        s = 'tsmin(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            self.indata[s].append(np.min(np.array(self.indata[keyname][-n::]), axis=0))
        else:
            pass
        return s

    def lowday(self, keyname, n, isinit=False):
        s = 'lowday(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            self.indata[s].append(np.argmin(np.array(self.indata[keyname][-n::]), axis=0))
        else:
            pass
        return s

    def highday(self, keyname, n, isinit=False):
        s = 'highday(' + keyname + ',' + str(n) + ')'
        n = int(round(n))
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            self.indata[s].append(np.argmax(np.array(self.indata[keyname][-n::]), axis=0))
        else:
            pass
        return s

    def max(self, keynamex, keynamey, isinit=False):
        inkey = 'max' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(np.maximum(self.indata[keynamex][-1], self.indata[keynamey][-1]))
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(np.maximum(self.indata[keynamex][-1], keynamey))
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(np.maximum(keynamex, self.indata[keynamey][-1]))
            else:
                pass
            return inkey
        else:
            return np.maximum(keynamex, keynamey)

    def min(self, keynamex, keynamey, isinit=False):
        inkey = 'max' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(np.minimum(self.indata[keynamex][-1], self.indata[keynamey][-1]))
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(np.minimum(self.indata[keynamex][-1], keynamey))
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(np.minimum(keynamex, self.indata[keynamey][-1]))
            else:
                pass
            return inkey
        else:
            return np.minimum(keynamex, keynamey)

    def lessthan(self, keynamex, keynamey, isinit=False):
        inkey = 'lessthan' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        # return inf if divisor is 0
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] < self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] < keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex < self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex < keynamey)

    def greaterthan(self, keynamex, keynamey, isinit=False):
        inkey = 'greaterthan' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        # return inf if divisor is 0
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] > self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] > keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex > self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex > keynamey)

    def equal(self, keynamex, keynamey, isinit=False):
        inkey = 'equal' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        # return inf if divisor is 0
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] == self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] == keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex == self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex == keynamey)

    def notequal(self, keynamex, keynamey, isinit=False):
        inkey = 'notequal' + '(' + str(keynamex) + ',' + str(keynamey) + ')'
        # return inf if divisor is 0
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(keynamex, str) and isinstance(keynamey, str):
            flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(self.indata[keynamex][-1] != self.indata[keynamey][-1])
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(keynamex, str):
            if isinit == False or self.doinit(keynamex, inkey) == False:
                self.indata[inkey].append(self.indata[keynamex][-1] != keynamey)
            else:
                pass
            return inkey
        elif isinstance(keynamey, str):
            if isinit == False or self.doinit(keynamey, inkey) == False:
                self.indata[inkey].append(keynamex != self.indata[keynamey][-1])
            else:
                pass
            return inkey
        else:
            return (keynamex != keynamey)

    def also(self, keynamex, keynamey, isinit=False):
        inkey = "also(" + keynamex + "," + keynamey + ")"
        if isinit == False:
            del self.indata[inkey][0]
        flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
        if isinit == False or flag == 0:
            self.indata[inkey].append(self.indata[keynamex][-1] & self.indata[keynamey][-1])
        elif flag == 1:
            self.indata[inkey].append(None)
        else:
            pass
        return inkey

    def oror(self, keynamex, keynamey, isinit=False):
        inkey = "oror(" + keynamex + "," + keynamey + ")"
        if isinit == False:
            del self.indata[inkey][0]
        flag = self.doinit(keynamex, inkey) + self.doinit(keynamey, inkey)
        if isinit == False or flag == 0:
            self.indata[inkey].append(self.indata[keynamex][-1] | self.indata[keynamey][-1])
        elif flag == 1:
            self.indata[inkey].append(None)
        else:
            pass
        return inkey

    def condition(self, field1, field2, field3, isinit=False):
        inkey = "condition(" + str(field1) + "," + str(field2) + "," + str(field3) + ")"
        if isinit == False:
            del self.indata[inkey][0]
        if isinstance(field2, str) and isinstance(field3, str):
            flag = self.doinit(field2, inkey) + self.doinit(field3, inkey)
            if isinit == False or flag == 0:
                self.indata[inkey].append(
                    np.where(self.indata[field1][-1], self.indata[field2][-1], self.indata[field3][-1]))
            elif flag == 1:
                self.indata[inkey].append(None)
            else:
                pass
            return inkey
        elif isinstance(field2, str):
            if isinit == False or self.doinit(field2, inkey) == False:
                self.indata[inkey].append(np.where(self.indata[field1][-1], self.indata[field2][-1], field3))
            else:
                pass
            return inkey
        elif isinstance(field3, str):
            if isinit == False or self.doinit(field3, inkey) == False:
                self.indata[inkey].append(np.where(self.indata[field1][-1], field2, self.indata[field3][-1]))
            else:
                pass
            return inkey
        else:
            return np.where(self.indata[field1][-1], field2, field3)

    def decaylinear(self, keyname, n, isinit=False):
        s = 'decaylinear(' + keyname + ',' + str(n) + ')'
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            t = self.indata[keyname][-n] * 1
            for i in range(n - 1):
                t = t + self.indata[keyname][-(i + 1)] * (n - i)
            t = t * 2 / ((1 + n) * n)
            self.indata[s].append(t)
        else:
            pass
        return s

    def decayexp(self, keyname, f, n, isinit=False):
        s = 'decayexp(' + keyname + ',' + str(n) + ')'
        if isinit == False:
            del self.indata[s][0]
        if isinit == False or self.doinit(keyname, s, n - 1) == False:
            t = self.indata[keyname][-n] * (f ** (n - 1))
            z = f ** (n - 1)
            for i in range(n - 1):
                t = t + self.indata[keyname][-(i + 1)] * (f ** i)
                z = z + f ** i
            t = t / z
            self.indata[s].append(t)
        else:
            pass
        return s

    def sma(self,keyname,n,m,isinit=False):
        s= "sma("+keyname+str(n)+str(m)+")"
        if isinit==False:
            del self.indata[s][0]
        if isinit==False or self.doinit(keyname,s,1)==False:
            t= self.indata[s][-1]
            r= m*self.indata[keyname][-2]+(n-m)*t
            self.indata[s].append(r/n)
        else:
            pass
        return s
    
    def wma(self,keyname,n,isinit=False):
        s="wma("+keyname+str(n)+")"
        if isinit==False:
            del self.indata[s][0]
        if isinit==False or self.doinit(keyname,n-1)==False:
            a=np.array(self.indata[keyname][-n::])
            r= a[-1]*0.9*0
            for i in range(1,n):
                r=r+a[-(i+1)]*0.9*i
            self.indata[s].append(r)
        else:
            pass
        return s
            
            
    def tsregression(self, ky, kx, n, lag, retval, isinit=False):
        # Regression model y[t]= a+b*x[t-lag]
        # The values that can be returned (resid, a, b, estimate_of_y) are represented by 0, 1, 2, 3 respectively.
        # Parameter description: y is response variable, x is independent variable, n is regression sample size
        # lag is the number of delay days, retval controls return value
        inkey = "tsregression(" + ky + "," + kx + "," + str(n) + "," + str(lag) + "," + str(retval) + ")"
        n = int(round(n))
        lag = int(round(lag))
        if isinit == False:
            del self.indata[inkey][0]
        flag = self.doinit(kx, inkey, n - 1) + self.doinit(ky, inkey, n - 1)
        if isinit == False or flag == 0:
            ry = np.array(self.indata[ky][-n::])
            rx = np.array(self.indata[kx][-n::])
            in_len = len(self.indata[ky][-1])
            resid = []
            a = []
            b = []
            est_y = []
            for i in range(in_len):
                model = LinearRegression().fit(rx[:, i], ry[:, i])
                a.append(model.intercept_[0])
                b.append(model.coef_[0])
                pred = model.predict(rx[:, i])[0]
                rea = ry[-1, i]
                resid.append(rea - pred)
                est_y.append(pred)
            if retval == 0:
                self.indata[inkey].append(np.array(resid))
            elif retval == 1:
                self.indata[inkey].append(np.array(a))
            elif retval == 2:
                self.indata[inkey].append(np.array(b))
            elif retval == 3:
                self.indata[inkey].append(np.array(est_y))
            else:
                raise ValueError
        elif flag == 1:
            self.indata[inkey].append(None)
        else:
            pass
        return inkey

    #################################################################################################################

    def generate(self, alpha_vec, data, di):
        super(example, self).generate(alpha_vec, data, di)
        for field in self.basicfields:
            del self.indata[field][0]
            self.indata[field].append(data['essentials'][field][di - self.delay, :])
        if self.benchmark is not None:
            del self.indata['benchmarkopen'][0]
            del self.indata['benchmarkclose'][0]
            self.indata['benchmarkopen'].append(data[self.benchmark][di-self.delay,0])
            self.indata['benchmarkclose'].append(data[self.benchmark][di-self.delay,3])
        exec(self.gene_str)
        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di, :] == 1, data['tradable'][di, :] == 1)
        alpha_vec[ix] = self.indata[self.finalname][-1][ix]



