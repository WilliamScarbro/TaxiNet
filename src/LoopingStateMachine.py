import BayesianModel as BM
import PrismAST as PAST
from Util import *
import PrismExec as PE

import datetime
from dataclasses import dataclass

@dataclass
class PrismComponent:
    name    : str
    invars  : [str] # names of input PrismVars
    outvars : [str] # names of output PrismVars
    fail_states : [str]
    #  
    logic: ...  # : ([PrismVar],[PrismVar],[Int]) -> (Int -> [PrismTrans])


# 0: component 0
# 1: component 1
# ...
# loop_max: loop step
# loop_max+1: fail state 0
# ...
# pc_max: fail_state n-1
class PrismLoopingStateMachine:
    def __init__(self,module_name,version,components: [PrismComponent],statevars: [PAST.PrismVar],fail_states: [str]):
        self.module_name=module_name
        self.version=version
        self.components=components
        self.fail_states=fail_states
        self.filename = f"./bin/{self.module_name}-{self.version}.pm"
        self.written=False


        self.statevar_dict={pv.name:pv for pv in statevars}
        self.loop_max = len(self.components)
        self.fail_state_pc_dict = {fail_states[i]:self.loop_max+1+i for i in range(0,len(fail_states))}
        pc_max=self.loop_max+len(fail_states)
        
        pc_var = PAST.PrismVar("pc",0,pc_max,0,"program counter")
        loop_var = PAST.PrismVar("k",0,"N",1,"loop counter")

        self.pvars = statevars+[pc_var,loop_var]

        self.loop_step = PAST.PrismTrans(f"pc={self.loop_max} & k < N",[("(pc'=0) & (k'=k+1)",1)])
                                   
    def __str__(self):
        indent="  "
        variable_declr = composeLines(indent,self.pvars)
        pc_vals = list(range(0,self.loop_max))
        component_logics = [
            f"{indent}// {c.name}\n"+
            composeLines(indent,c.logic(
                mapL(dict_to_func(self.statevar_dict),c.invars),
                mapL(dict_to_func(self.statevar_dict),c.outvars),
                mapL(dict_to_func(self.fail_state_pc_dict),c.fail_states))(pc))
            for pc,c in zip(pc_vals,self.components)]
        loop_rep = composeLines(indent,[self.loop_step])
        
        pc_summary="// PC values:\n"
        for pc,c in zip(pc_vals,self.components):
            pc_summary+=f"//   {pc} : {c.name}\n"
        pc_summary+=f"//   {self.loop_max} : Loop Logic\n"
        for i in range(len(self.fail_states)):
            pc_summary+=f"//   {self.loop_max+1+i} : {self.fail_states[i]}\n"
            
        cl_rep = ""
        for cl in component_logics:
            cl_rep+=cl+"\n"
                    
        return f"""
// {self.module_name}
// Prism Looping State Machine
// Generated: {datetime.datetime.now()}
{pc_summary}

dtmc

const N;

module {self.module_name}

{variable_declr}

{cl_rep}

  // Loop Logic
{loop_rep}

endmodule
"""

    def save_to_file(self):
        if self.written:
            return
        self.written=True
        # print("writing to "+self.filename)
        with open(self.filename, "wt") as f:
            f.write(str(self))


    def test_property(self,prism_property,consts):
        if not self.written:
            self.save_to_file()
        return PE.run_prism(self.filename,prism_property.filename,1,consts)

    
## Component Builders

def define_component_by_enumeration(var_list,func,pc):
    transitions=[]
    vl_enum = PAST.var_list_to_enumerable(var_list)
    for pv_assign in vl_enum.enumerate_pv():
        condition = ""
        for pv,val in pv_assign:
            condition+=f"{pv}={val} & "
        condition=condition[:-2]
        pt = PAST.PrismTrans(condition,func(pv_assign))
        pt.addPC(pc)
        transitions.append(pt)
    return transitions


# Perceiver from BayesianModel

# (((state, state_est) -> Prob),  PrismVar) -> (VarInst -> [Assignment])
def perceive_func_from_read_func(read_func,est_var):
    def perceive_func(args):
        state=args[0][1]
        return [(f"({est_var.name}'={est})",read_func(state,est)) for est in range(est_var.low,est_var.high+1)]
    return perceive_func

# BayesianNetworkWrapper -> ([PrismVar],[PrismVar],[Int]) -> (PC -> [PrismTrans])
def perceiver_from_est_model(model):
    read_func = BM.read_conf_mat(model)  # :: (state,state_est) -> prob
    
    def perceiver(state,state_est,_):

        def perceiver_pc(pc):

            return PAST.define_component_by_enumeration(
                state,
                perceive_func_from_read_func(read_func,state_est[0]),
                pc)
        
        return perceiver_pc

    return perceiver
