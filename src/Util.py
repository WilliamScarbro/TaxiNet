def composeLines(indent,pts):
    res=""
    for pt in pts:
        res+=indent+str(pt)+"\n"
    return res

def mapL(f,a):
    return [f(ai) for ai in a]

def dict_to_func(d):
    return lambda x : d[x]
