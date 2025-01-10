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


class PrismProp:
    def __init__(self,rep,filename):
        self.rep=rep
        self.filename=filename
        with open(self.filename,"w") as pfile:
            pfile.write(rep)
