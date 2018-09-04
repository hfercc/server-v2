import sys
sys.path.append('./lib')
import numpy as np
from alpha import alpha

def create():
    return dummy_alpha_equalweight()

class dummy_alpha_equalweight(alpha):
    """description of class"""
    def __init__(self, *args, **kwargs):
        super(dummy_alpha_equalweight, self).__init__(*args, **kwargs)

    def initialize(self):
        super(dummy_alpha_equalweight, self).initialize()

    def generate(self, alpha_vec, data, di):
        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di, :] == 1, data['tradable'][di, :] == 1)

        alpha_vec[ix] = [1 for i in range(alpha_vec[ix].shape[0])]