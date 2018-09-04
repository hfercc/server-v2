import numpy as np
from alpha import alpha

def create():
    return dummy_alpha()

class dummy_alpha(alpha):
    """description of class"""
    def __init__(self, *args, **kwargs):
        super(dummy_alpha, self).__init__(*args, **kwargs)

    def generate(self, alpha_vec, data, di):
        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di, :] == 1, data['tradable'][di, :] == 1)

        alpha_vec[ix] = data['essentials']['open'][di-self.delay, ix] \
            / data['essentials']['close'][di-self.delay-1, ix]