import numpy as np
from alpha_cached import alpha_cached

def create():
    return alpha_template()

class alpha_template(alpha_cached):
    """description of class"""
    def __init__(self, *args, **kwargs):
        super(alpha_template, self).__init__(*args, **kwargs)        
        ## write your code below

    def initialize(self):
        super(alpha_template, self).initialize()
        ## write your code below

    def on_start(self, data, start_di):
        super(alpha_template, self).on_start(data, start_di)
        ## write your code below

    def generate(self, alpha_vec, data, di):
        super(alpha_template, self).generate(alpha_vec, data, di)

        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di, :] == 1, data['tradable'][di, :] == 1)

        #alpha_vec[ix] = 
