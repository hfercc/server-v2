import sys
import pandas as pd
from scipy.stats.stats import pearsonr
import numpy as np
import time
import timeit
from alpha import alpha

def create():
    return dummy_alpha()

class dummy_alpha(alpha):
    """description of class"""
    def __init__(self, *args, **kwargs):
        super(dummy_alpha, self).__init__(*args, **kwargs)        
        self.prev_n = 10

    def initialize(self):
        super(dummy_alpha, self).initialize()
        if 'prev_n' in self.params:
            self.prev_n = int(self.params['prev_n'])

    def generate(self, alpha_vec, data, di):
        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di-1, :] == 1, data['tradable'][di-1, :] == 1)

        for tk in range(alpha_vec.shape[0]):
            if ix[tk]:
                if data['universe'][di-self.delay, tk] == 1 and data['tradable'][di-self.delay, tk]:
                    alpha_vec[tk] = -1 * pearsonr(data['essentials']['vwap'][di-self.prev_n:di, tk], data['essentials']['volume'][di-self.prev_n:di, tk])[0]
