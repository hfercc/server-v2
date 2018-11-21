import sys
import numpy as np
from alpha import alpha

def create():
    return dummy_random()

class dummy_random(alpha):
    """description of class"""
    def __init__(self, *args, **kwargs):
        super(dummy_random, self).__init__(*args, **kwargs)        

    def initialize(self):
        super(dummy_random, self).initialize()

    def generate(self, alpha_vec, data, di):
        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di-1, :] == 1, data['tradable'][di-1, :] == 1)

        alpha_vec[ix] = np.random.random(len(alpha_vec[ix]))
