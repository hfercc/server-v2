import numpy as np
from alpha import alpha

def create():
    return alpha_template()

class alpha_template(alpha):
    """description of class"""
    def __init__(self, *args, **kwargs):
        super(alpha_template, self).__init__(*args, **kwargs)        

    def initialize(self):
        super(alpha_template, self).initialize()

    def generate(self, alpha_vec, data, di):
        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di, :] == 1, data['tradable'][di, :] == 1)

        #alpha_vec[ix] = 