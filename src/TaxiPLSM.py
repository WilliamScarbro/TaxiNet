import PrismAST as PAST
import LoopingStateMachine as PLSM
import BayesianModel as BM
import ConfMatModel as CMM
import CorrErrModel as CEM

## Controller

def control_func(args):
    cte=args[0][1]
    he=args[1][1]
        
    if cte==0:
        a=-he
    else:
        cte_sign = int(cte / abs(cte))
        if cte_sign*he == -1:
            a=0
        else:
            a=-cte_sign
            
    return [(f"(a'={a})",1)]

def control(state_est,*_):
    return lambda pc : PLSM.define_component_by_enumeration(state_est,control_func,pc)


## Dynamics

def dynamics(_,__,fail_states):
    def dynamic_func(pc):
        return [PAST.PrismTrans(f"cte>=-2 & cte<=2 & he>=-1 & he<=1 & pc={pc}",[(f"(he'=he+a) & (cte'=cte+he+a) & (pc'={pc+1})",1)]),
                PAST.PrismTrans(f"(cte< -2 | cte>2 | he< -1 | he>1) & pc={pc}",[(f"(pc'={fail_states[0]})",1)])]
    return dynamic_func


## Aborter

def aborter(state,_,fail_states):
    # should use enum_low and enum_high rather than hardcoding  
    return lambda pc : [
        PAST.PrismTrans(f"(cte< -2 | cte>2) & pc={pc}",[(f"(pc'={fail_states[0]})",1)]),
        PAST.PrismTrans(f"(he< -1 | he>1) & pc={pc}",[(f"(pc'={fail_states[1]})",1)]),
        PAST.PrismTrans(f"cte>=-2 & cte<=2 & he>=-1 & he<=1 & pc={pc}",[(f"(pc'={pc+1})",1)])
    ]


def create_TaxiPLSM_CM(label,cte_sample_file,he_sample_file):
    cte = PAST.PrismVar("cte",-4,4,0,enum_low=-2,enum_high=2)
    he = PAST.PrismVar("he",-2,2,0,enum_low=-1,enum_high=1)
    cte_est = PAST.PrismVar("cte_est",-2,2,0)
    he_est = PAST.PrismVar("he_est",-1,1,0)
    a = PAST.PrismVar("a",-1,1,0)
    variables=[cte,he,cte_est,he_est,a]
    
    cte_model = CMM.ConfusionMatrix(cte_sample_file)
    he_model = CMM.ConfusionMatrix(he_sample_file)
    
    state=["cte","he"]
    state_est=["cte_est","he_est"]
    action=["a"]
    fail_states=["cte_fail","he_fail","dyn_fail"]
    
    taxiP_cte = PLSM.PrismComponent("Perceiver (CTE)",["cte"],["cte_est"],[],cte_model.perceiver_from_est_model())
    taxiP_he = PLSM.PrismComponent("Perceiver (HE)",["he"],["he_est"],[],he_model.perceiver_from_est_model())
    taxiC = PLSM.PrismComponent("Controller",state_est,action,[],control)
    taxiD = PLSM.PrismComponent("Dynamics",state+action,state,["dyn_fail"],dynamics)
    taxiA = PLSM.PrismComponent("Aborter",state,[],fail_states[:2],aborter)
    components=[taxiP_cte,taxiP_he,taxiC,taxiD,taxiA]
    

    return PLSM.PrismLoopingStateMachine("TaxiConfMat",label,components,variables,fail_states)


def create_TaxiPLSM_CE(label,cte_sample_file,he_sample_file):
    cte = PAST.PrismVar("cte",-4,4,0,enum_low=-2,enum_high=2)
    he = PAST.PrismVar("he",-2,2,0,enum_low=-1,enum_high=1)
    cte_pe = PAST.PrismVar("cte_pe",-4,4,0)
    he_pe = PAST.PrismVar("he_pe",-2,2,0)
    cte_est = PAST.PrismVar("cte_est",-2,2,0)
    he_est = PAST.PrismVar("he_est",-1,1,0)
    a = PAST.PrismVar("a",-1,1,0)
    variables=[cte,he,cte_pe,he_pe,cte_est,he_est,a]
    
    cte_model = CEM.CorrErrModel(cte_sample_file)
    # print(f"cte error correlation: {cte_model.error_corr()}")
    # print(cte_model.model.get_cpds('obs'))
    he_model = CEM.CorrErrModel(he_sample_file)
    # print(f"he error correlation: {he_model.error_corr()}")
    
    state=["cte","he"]
    p_error=["cte_pe","he_pe"]
    state_est=["cte_est","he_est"]
    action=["a"]
    fail_states=["cte_fail","he_fail","dyn_fail"]
    
    taxiP_cte = PLSM.PrismComponent("Perceiver (CTE)",["cte","cte_pe"],["cte_est"],[],cte_model.perceiver_from_est_model())
    taxiP_he = PLSM.PrismComponent("Perceiver (HE)",["he","he_pe"],["he_est"],[],he_model.perceiver_from_est_model())
    taxiC = PLSM.PrismComponent("Controller",state_est,action,[],control)
    taxiD = PLSM.PrismComponent("Dynamics",state+action,state,["dyn_fail"],dynamics)
    taxiA = PLSM.PrismComponent("Aborter",state,[],fail_states[:2],aborter)
    components=[taxiP_cte,taxiP_he,taxiC,taxiD,taxiA]
    

    return PLSM.PrismLoopingStateMachine("TaxiCorrErr",label,components,variables,fail_states)


import argparse

def main():
    parser = argparse.ArgumentParser(description="CLI for handling model inputs with required flags.")

    parser.add_argument("--cte", required=True, type=str, help="Filename of cte sample")
    parser.add_argument("--he", required=True, type=str, help="Filename of he sample")
    parser.add_argument("--label", "-l", required=True, type=str, help="Instance label, used to differentiate models with distinct data")
    parser.add_argument("--model", "-m", required=True, type=str, help="Prism model name")

    # Parse arguments
    args = parser.parse_args()


    models = {"CorrErr":create_TaxiPLSM_CE,
              "ConfMat":create_TaxiPLSM_CM}
    if not args.model in models:
        print(f"Unknown model {args.model}\n  Known models {models.keys()}")
        exit(1)

    plsm = models[args.model](args.label,args.cte,args.he)
    print(f"writing to {plsm.filename}")
    plsm.save_to_file()

if __name__=="__main__":
    main()
