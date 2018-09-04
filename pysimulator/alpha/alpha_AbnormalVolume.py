import sys
sys.path.append('./lib')
import numpy as np
from alpha import alpha

def create():
    return alpha_AbnormalVolume()

class alpha_AbnormalVolume(alpha):
    """description of class"""
    def __init__(self, *args, **kwargs):
        super(alpha_AbnormalVolume, self).__init__(*args, **kwargs)
        self.prev_n = 10

    def initialize(self):
        super(alpha_AbnormalVolume, self).initialize()
        if 'prev_n' in self.params:
            self.prev_n = int(self.params['prev_n'])

    def generate(self, alaph_vec, data, di):
        # get stocks that are tradable in the given universe
        ix = np.logical_and(data['universe'][di, :] == 1, data['tradable'][di, :] == 1)

        alaph_vec[ix] = -1 * data['essentials']['volume'][di-self.delay, ix] \
            / np.nanmean(data['essentials']['volume'][di-self.prev_n:di, ix])

        ## The following code runs much slower than the above vectorized code
        ## Please try your best to write code in vectorized format
        ## You can try these two code snippets to see the difference

        #for i in range(alaph_vec.shape[0]):
        #    alaph_vec[i] = -1 * data['essentials']['volume'][di-self.delay, i] \
        #        / np.nanmean(data['essentials']['volume'][di-self.delay-self.prev_n:di-self.delay, i])

