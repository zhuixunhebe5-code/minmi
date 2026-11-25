import requests, json, time
from concurrent.futures import ThreadPoolExecutor

S = requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0"})
URL = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD"
       "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,REPORTDATE,PARENT_NETPROFIT,SJLTZ"
       "&filter=(SECURITY_CODE%3D%22{code}%22)(REPORTDATE%3D%27{rd}%27)&pageNumber=1&pageSize=5")

def get(code, rd):
    for _ in range(3):
        try:
            r = S.get(URL.format(code=code, rd=rd), timeout=20).json()
            if r.get("result") and r["result"]["data"]:
                return r["result"]["data"][0]
        except Exception:
            time.sleep(0.6)
    return None

d = json.load(open("with_industry.json"))
for x in d:
    x["chg_close"] = round((x["last_close"]/x["start_close"]-1)*100, 2)

def tech(x):
    ind = x["industry"].split("|"); l1 = ind[0] if ind else ""
    return l1 in ("电子","计算机","通信") or (l1=="国防军工" and len(ind)>1 and "军工电子" in ind[1]) \
           or l1=="电力设备" or (l1=="传媒" and len(ind)>1 and "游戏" in ind[1])

pool = [x for x in d if tech(x) and x["chg_close"] <= -50]
print("待查财报:", len(pool))

def work(x):
    q3 = get(x["code"], "2026-09-30")
    h1 = get(x["code"], "2026-06-30")
    x["np_q3cum"] = q3["PARENT_NETPROFIT"]/1e8 if q3 else None
    x["np_h1"] = h1["PARENT_NETPROFIT"]/1e8 if h1 else None
    x["sjltz"] = q3.get("SJLTZ") if q3 else None
    if x["np_q3cum"] is not None and x["np_h1"] is not None:
        x["np_q3_single"] = round(x["np_q3cum"]-x["np_h1"], 4)
    else:
        x["np_q3_single"] = None
    return x

with ThreadPoolExecutor(max_workers=6) as ex:
    out = list(ex.map(work, pool))

json.dump(out, open("with_profit.json","w"), ensure_ascii=False)
for x in sorted(out, key=lambda y: y["chg_close"]):
    print(f'{x["code"]} {x["name"]:<7} {x["chg_close"]:>7}% | 前三季净利 {x["np_q3cum"] if x["np_q3cum"] is not None else "NA":>10} 亿 | Q3单季 {x["np_q3_single"] if x["np_q3_single"] is not None else "NA":>9} | 同比 {x["sjltz"]}')
