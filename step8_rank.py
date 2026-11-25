import json
d=json.load(open("score_raw.json"))

def clip(v,lo,hi):
    return max(lo,min(hi,v))

def norm(vals, reverse=False):
    lo,hi=min(vals),max(vals)
    if hi==lo: return [50.0]*len(vals)
    out=[(v-lo)/(hi-lo)*100 for v in vals]
    return [100-x for x in out] if reverse else out

for x in d:
    x["sj_c"]=clip(x["sjltz"],-100,300)
    x["ys_c"]=clip(x["ystz"],-50,100)

np_s   = norm([x["np"] for x in d])
roe_s  = norm([x["roe"] for x in d])
gm_s   = norm([x["xsmll"] for x in d])
ys_s   = norm([x["ys_c"] for x in d])
sj_s   = norm([x["sj_c"] for x in d])
ocf_s  = norm([x["ocf"] for x in d])
dar_s  = norm([x["dar"] for x in d], reverse=True)
pe_s   = norm([x["pe"] if (x["pe"] and x["pe"]>0) else 999 for x in d], reverse=True)

W={"np":0.20,"roe":0.15,"gm":0.10,"ys":0.10,"sj":0.15,"ocf":0.15,"dar":0.10,"pe":0.05}
for i,x in enumerate(d):
    x["s"]={"np":np_s[i],"roe":roe_s[i],"gm":gm_s[i],"ys":ys_s[i],
            "sj":sj_s[i],"ocf":ocf_s[i],"dar":dar_s[i],"pe":pe_s[i]}
    x["total"]=round(sum(x["s"][k]*w for k,w in W.items()),1)

d.sort(key=lambda y:-y["total"])
print(f'{"排名":<4}{"代码":<8}{"名称":<8}{"总分":>6}{"盈利":>6}{"ROE":>6}{"毛利":>6}{"营收增":>7}{"净利增":>7}{"现金流":>7}{"负债":>6}{"估值":>6}')
for i,x in enumerate(d,1):
    s=x["s"]
    print(f'{i:<4}{x["code"]:<8}{x["name"]:<8}{x["total"]:>6}{s["np"]:>6.0f}{s["roe"]:>6.0f}{s["gm"]:>6.0f}{s["ys"]:>7.0f}{s["sj"]:>7.0f}{s["ocf"]:>7.0f}{s["dar"]:>6.0f}{s["pe"]:>6.0f}')
json.dump(d,open("ranked.json","w"),ensure_ascii=False)
