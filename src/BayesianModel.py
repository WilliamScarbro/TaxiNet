
import numpy as np
import pandas as pd
from pgmpy.models import BayesianNetwork
from pgmpy.inference import VariableElimination
from abc import ABC, abstractmethod

import DataLoader as DL
import PrismAST as PAST
import LoopingStateMachine as PLSM

class BayesianNetworkWrapper:
    def __init__(self,nodes,edges):
        self.nodes=nodes
        self.edges=edges
        self.model=BayesianNetwork(edges)
        
    def fit(self,observations):
        df = pd.DataFrame(data=observations,columns=self.nodes)
        self.model.fit(df)
        assert self.model.check_model
        
    def query(self,variables,evidence):
        inference = VariableElimination(self.model)
        return inference.query(variables=variables, evidence=evidence)

    def read_model(self):
        pass

    def perceive_func_from_read_func(self,state_est):
        pass

    # a generic way of defining a Perceiver component from Bayesian model
    #   customized by read_model and perceive_func_form_read_func
    # BayesianNetworkWrapper -> ([PrismVar],[PrismVar],[Int]) -> (PC -> [PrismTrans])
    def perceiver_from_est_model(self):
        read_func = self.read_model()

        def perceiver(state,state_est,_):
    
            def perceiver_pc(pc):
    
                return PLSM.define_component_by_enumeration(
                    state,
                    self.perceive_func_from_read_func(state_est),
                    pc)
            
            return perceiver_pc
    
        return perceiver


if __name__=="__main__":
    conf_model = conf_model_from_csv("he_sample.csv")
    print(conf_model.model.get_cpds('obs').to_factor().get_value(gt="2",obs="1"))
