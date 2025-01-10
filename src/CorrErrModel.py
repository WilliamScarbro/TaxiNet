import BayesianModel as BM
import DataLoader as DL
from Util import *

import numpy as np
from scipy.stats import pearsonr


## Model: (PE,GT) -> OBS

class CorrErrModel(BM.BayesianNetworkWrapper):
    def __init__(self, sample_file, min_filter=None):
        self.min_filter = min_filter
        self.sample = DL.read_csv_as_pairs(sample_file)

        # add PrevErr and CurErr values
        self.error_sample=gt_obs_to_error(self.sample)
        
        nodes = ["pe","gt","obs","ce"]
        edges = [("pe","ce"),
                 ("gt","obs"),
                 ("pe","obs")]
        super().__init__(nodes,edges)
        self.fit(mapL(lambda pgoc : tuple(str(e) for e in pgoc),self.error_sample))
        
    def read_model(self):
        def from_model(gt,pe,obs):
            # print("pe_model: ",gt,pe,obs)
            return self.model.get_cpds("obs").to_factor().get_value(pe=str(pe),gt=str(gt),obs=str(obs))
        return from_model

    def error_corr(self):
        pe = mapL(lambda s:s[0], self.error_sample)
        ce = mapL(lambda s:s[3], self.error_sample)
        return pearsonr(pe,ce)[0]
        # print(corr,pval)
        # return calculate_correlation(self.model.get_cpds('ce'))['pe']



    # Used by define_component_by_enumeration in BayesianNetworkWrapper.perceiver_from_est_model
    # uses min_filter to remove zeros
    # (CorrErrModel, [PrismVar]) -> ((VarInst,VarInst) -> [Assignment])
    def perceive_func_from_read_func(self,est_vars):
        est_var=est_vars[0]
        def perceive_func(args):
            state=args[0][1]
            p_error=args[1][1]
            p_error_name=args[1][0]
            
            est_probs = [(est,self.read_model()(state,p_error,est))
                         for est in range(est_var.low,est_var.high+1)]

            if not (self.min_filter is None):
                est_probs = filter(lambda est_prob : est_prob[1] > self.min_filter, est_probs)

            return list(map(lambda est_prob: (f"({est_var.name}'={int(est_prob[0])}) & ({p_error_name}'={int(state-est_prob[0])})",est_prob[1]),est_probs))
        return perceive_func

def gt_obs_to_error(sample):
    res=[]
    pe=0
    for c in sample:
        gt=int(c[0])
        obs=int(c[1])
        ce=gt-obs
        res.append((pe,gt,obs,ce))
        pe=ce
    return res


if __name__=="__main__":
    import sys
    cem = CorrErrModel(sys.argv[1])
    print(cem.error_corr())
