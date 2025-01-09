import BayesianModel as BM
import DataLoader as DL

import numpy as np
from scipy.stats import pearsonr


## Model: (PE,GT) -> OBS

class CorrErrModel(BM.BayesianNetworkWrapper):
    def __init__(self, sample_file, min_filter=None):
        self.min_filter = min_filter
        sample = DL.read_csv_as_pairs(sample_file)
        def gt_obs_to_error(sample):
            res=[]
            pe="0"
            for c in sample:
                ce=str(int(c[1])-int(c[0]))
                res.append((pe,c[0],c[1],ce))
                pe=ce
            return res
            
        error_sample=gt_obs_to_error(sample)
        
        # includes PE->CE cpd to assess correlation
        nodes = ["pe","gt","obs","ce"]
        edges = [("pe","ce"),
                 ("gt","obs"),
                 ("pe","obs")]
        super().__init__(nodes,edges)
        self.fit(error_sample)
    
    def read_model(self):
        def from_model(gt,pe,obs):
            # print("pe_model: ",gt,pe,obs)
            return self.model.get_cpds("obs").to_factor().get_value(pe=str(pe),gt=str(gt),obs=str(obs))
        return from_model

    def error_corr(self):
        return calculate_correlation(self.model.get_cpds('ce'))



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
 

# Generated by 4o
def weighted_pearsonr(x, y, weights):
    """
    Calculate the weighted Pearson correlation coefficient between two variables.

    :param x: Array of values for the first variable.
    :param y: Array of values for the second variable.
    :param weights: Array of weights corresponding to the values.
    :return: Weighted Pearson correlation coefficient.
    """
    # Convert inputs to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)
    weights = np.asarray(weights)
    
    # Weighted means
    mean_x = np.average(x, weights=weights)
    mean_y = np.average(y, weights=weights)
    
    # Weighted covariance and variances
    cov_xy = np.average((x - mean_x) * (y - mean_y), weights=weights)
    var_x = np.average((x - mean_x) ** 2, weights=weights)
    var_y = np.average((y - mean_y) ** 2, weights=weights)
    
    # Pearson correlation
    return cov_xy / np.sqrt(var_x * var_y)

def calculate_correlation(cpd):
    """
    Calculate the correlation between a variable and its parent(s) based on a CPD table.

    :param cpd: TabularCPD object from pgmpy
    :return: A dictionary with correlations between the variable and each parent.
    """
    evidence = cpd.variables[1:]
    evidence_card = cpd.cardinality[1:]

    # Check if the CPD has parents
    parents = evidence # cpd.get_evidence()
    if not parents:
        raise ValueError("The CPD has no parents. Correlation cannot be calculated.")
    
    # Extract CPD values
    values = cpd.values
    
    # Get the variable and its metadata
    variable = cpd.variable
    variable_card = cpd.variable_card
    parent_card = evidence_card #cpd.get_evidence_card()
    
    # Create all possible parent combinations
    parent_states = np.array(np.meshgrid(*[range(c) for c in parent_card])).T.reshape(-1, len(parents))
    
    # Flatten the CPD to get joint probabilities
    joint_probs = values.flatten()
    
    # Repeat the child states for each parent combination
    child_states = np.repeat(np.arange(variable_card), len(joint_probs) // variable_card)
    
    # Calculate correlations between the child variable and each parent
    correlations = {}
    for i, parent in enumerate(parents):
        parent_values = np.tile(parent_states[:, i], variable_card)
        correlation = weighted_pearsonr(parent_values, child_states, joint_probs)
        correlations[parent] = correlation

    return correlations


