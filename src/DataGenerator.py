import random
def mk_uncor_sample(n,span):
    res=[]
    vals=[i for i in range(-span,span+1)]
    for i in range(n):
        gt=random.choice(vals)
        obs=random.choice(vals)
        res.append((gt,obs))
    return res

def mk_cor_sample(n,span,pos=True):
    res=[]
    pe=0
    vals=[i for i in range(-span,span+1)]
    for i in range(n):
        gt=random.choice(vals)
        obs=random.choice(vals)
        if (not pos and pe<0) or (pos and pe>0):
            obs=random.choice([obs,obs-1 if obs>-span else obs])
        if (not pos and pe>0) or (pos and pe<0):
            obs=random.choice([obs,obs+1 if obs<span else obs])
        pe=gt-obs
        res.append((gt,obs))
    return res

def write_sample(sample,filename):
    with open(filename,"w") as file:
        contents=""
        for (gt,he) in sample:
            contents+=f"{gt},{he}\n"
        file.write(contents) 

def generate():
    cte_pcor_sample=mk_cor_sample(1000,2,pos=True)
    write_sample(cte_pcor_sample,"./lib/cte_corr_pos.csv")

    he_pcor_sample=mk_cor_sample(1000,1,pos=True)
    write_sample(he_pcor_sample,"./lib/he_corr_pos.csv")

    cte_ncor_sample=mk_cor_sample(1000,2,pos=False)
    write_sample(cte_ncor_sample,"./lib/cte_corr_neg.csv")

    he_ncor_sample=mk_cor_sample(1000,1,pos=False)
    write_sample(he_ncor_sample,"./lib/he_corr_neg.csv")

    cte_uncor_sample=mk_uncor_sample(1000,2)
    write_sample(cte_uncor_sample,"./lib/cte_uncorr.csv")

    he_uncor_sample=mk_uncor_sample(1000,1)
    write_sample(he_uncor_sample,"./lib/he_uncorr.csv")

    
if __name__=="__main__":
    generate()
