import sys
import numpy as np
from scipy.stats.stats import pearsonr
import copy
from alpha import alpha

def create():
    return alpha_PriceSwingDiv()

class alpha_PriceSwingDiv(alpha):
    """description of class"""
    def __init__(self, *args, **kwargs):
        super(alpha_PriceSwingDiv, self).__init__(*args, **kwargs)
        self.prev_n = 10
        

    def initialize(self):
        super(alpha_PriceSwingDiv, self).initialize()
        if 'prev_n' in self.params:
            self.prev_n = int(self.params['prev_n'])      
            
    def generate(self, alaph_vec, data, di):
        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di-1, :] == 1, data['tradable'][di-1, :] == 1)
        
        for i in range(alaph_vec.shape[0]):
            if ix[i]:
                if data['universe'][di-self.delay, i] == 1 and data['tradable'][di-self.delay, i]:
                    alaph_vec[i] = -1 * pearsonr(data['essentials']['high'][di-self.prev_n:di,i] / data['essentials']['low'][di-self.prev_n:di,i], \
                        data['essentials']['volume'][di-self.prev_n:di,i])[0]
