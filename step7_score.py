import requests, json, time
from concurrent.futures import ThreadPoolExecutor

S = requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0"})
U = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD"
     "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,PARENT_NETPROFIT,YSTZ,SJLTZ,WEIGHTAVG_ROE,XSMLL,MGJYXJJE"
     "&filter=(SECURITY_CODE%3D%22{code}%22)(REPORTDATE%3D%272026-09-30%27)&pageNumber=1&pageSize=3")
U2 = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DMSK_FN_BALANCE"
      "&columns=SECURITY_CODE,DEBT_ASSET_RATIO&filter=(SECURITY_CODE%3D%22{code}%22)(REPORT_DATE%3D%272026-09-30%27)&pageNumber=1&pageSize=3")

codes=["688388","600577","300660","300102","603881","688208","002531","603005","002245"]

def g(u):
    for _ in range(3):
        try:
            r=S.get(u,timeout=20).json()
            if r.get("result") and r["result"]["data"]: return r["result"]["data"][0]
        except Exception: time.sleep(0.6)
    return {}

def work(c):
    a=g(U.format(code=c)); b=g(U2.format(code=c))
    return {"code":c,"name":a.get("SECURITY_NAME_ABBR"),
            "np":(a.get("PARENT_NETPROFIT") or 0)/1e8,
            "ystz":a.get("YSTZ"),"sjltz":a.get("SJLTZ"),
            "roe":a.get("WEIGHTAVG_ROE"),"xsmll":a.get("XSMLL"),
            "ocf":a.get("MGJYXJJE"),"dar":b.get("DEBT_ASSET_RATIO")}

with ThreadPoolExecutor(max_workers=5) as ex:
    res=list(ex.map(work,codes))

cand={x["code"]:x for x in json.load(open("cand.json"))}
for x in res:
    c=cand.get(x["code"],{})
    x["price"]=c.get("price"); x["mktcap"]=c.get("mktcap_yi"); x["pe"]=c.get("pe")
json.dump(res,open("score_raw.json","w"),ensure_ascii=False)
for x in res:
    print(x)
