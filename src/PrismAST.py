from dataclasses import dataclass
from Util import *

# simple representation of Prism in python

# <name> : [<low>..<high>] init <init>
class PrismVar:
    def __init__(self,name,low,high,init,desc=None,enum_low=None,enum_high=None):
        self.name=name
        self.low=low
        self.high=high
        self.init=init
        self.desc=desc
        
        # when defining components by enumeration, only certain (legal) values should be considered
        # this is a kludge and lacks generality (what if two components need to enumerate differently?)
        self.enum_low= low if enum_low is None else enum_low
        self.enum_high= high if enum_high is None else enum_high
    def __str__(self):
        return f"{self.name} : [{self.low}..{self.high}] init {self.init};"+(f" // {self.desc}" if self.desc else "")
    def enumerate_pv(self):
        return [[(self.name,i)] for i in range(self.enum_low,self.enum_high+1)]

# combines enumeration domain of two PrismVars (or PrismVar with EnumerablePair, etc.)
# used by define_component_by_enumeration
class EnumerablePair:
    def __init__(self,a,b):
        self.a=a
        self.b=b
    def enumerate_pv(self):
        ae=self.a.enumerate_pv()
        be=self.b.enumerate_pv()
        return [ae_vals+be_vals for ae_vals in ae for be_vals in be]
    def __str__(self):
        return f"EP( {str(self.a)}, {str(self.b)})"

# builds EnumerablePair for PrismVar list
def var_list_to_enumerable(var_list : [PrismVar]):
    if len(var_list)==0:
        return PrismVar("-empty-var-",0,-1,0) # empty enumeration
    if len(var_list)==1:
        return var_list[0]
    if len(var_list)>=2:
        return EnumerablePair(var_list[0],var_list_to_enumerable(var_list[1:]))

# [] <condition> -> <results[0][1]> : <results[0][0]> + <results[1][1]> : <results[1][0]> + ...
class PrismTrans:
    def __init__(self,condition,results,withpc=False):
        self.condition=condition # str
        self.results=results # [(str,prob)]
        assert self.results # cannot be empty
        self.withpc=False
    def __str__(self):
        res = f"[] {self.condition} -> "
        for trans,prob in self.results:
            res+=f"{prob} : {trans} + "
        res=res[:-2]+";"
        return res
    def addPC(self,pc):
        if self.withpc:
            return
        self.withpc=True
        self.condition += f" & pc={pc}"
        self.results =  [(r+f" & (pc'={pc+1})",prob) for r,prob in self.results]
        return self



@dataclass
class PrismComponent:
    name    : str
    invars  : [str] # names of input PrismVars
    outvars : [str] # names of output PrismVars
    fail_states : [str]
    #  
    logic: ...  # : ([PrismVar],[PrismVar],[Int]) -> (Int -> [PrismTrans])


def define_component_by_enumeration(var_list,func,pc):
    transitions=[]
    vl_enum = var_list_to_enumerable(var_list)
    for pv_assign in vl_enum.enumerate_pv():
        condition = ""
        for pv,val in pv_assign:
            condition+=f"{pv}={val} & "
        condition=condition[:-2]
        pt = PrismTrans(condition,func(pv_assign))
        pt.addPC(pc)
        transitions.append(pt)
    return transitions

# 0: component 0
# 1: component 1
# ...
# loop_max: loop step
# loop_max+1: fail state 0
# ...
# pc_max: fail_state n-1
class PrismLoopingStateMachine:
    def __init__(self,module_name,version,components: [PrismComponent],statevars: [PrismVar],fail_states: [str]):
        self.module_name=module_name
        self.version=version
        self.components=components

        self.statevar_dict={pv.name:pv for pv in statevars}
        self.loop_max = len(self.components)
        self.fail_state_pc_dict = {fail_states[i]:self.loop_max+1+i for i in range(0,len(fail_states))}
        pc_max=self.loop_max+len(fail_states)
        
        pc_var = PrismVar("pc",0,pc_max,0,"program counter")
        loop_var = PrismVar("k",0,"N",1,"loop counter")

        self.pvars = statevars+[pc_var,loop_var]

        self.loop_step = PrismTrans(f"pc={self.loop_max} & k < N",[("(pc'=0) & (k'=k+1)",1)])
                                   
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
        

        cl_rep = ""
        for cl in component_logics:
            cl_rep+=cl+"\n"
                    
        return f"""
dtmc

const N;

module {self.module_name}

{variable_declr}

{cl_rep}

  // loop step
{loop_rep}

endmodule
"""

    def save_to_file(self):
        filename=f"./bin/{self.module_name}-{self.version}.pm"
        print("writing to "+filename)
        with open(filename, "wt") as f:
            f.write(str(self))
