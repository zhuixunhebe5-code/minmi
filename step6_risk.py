import requests, json, time
from concurrent.futures import ThreadPoolExecutor

S = requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0"})
U1 = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD"
      "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,PARENT_NETPROFIT,SJLTZ,MGJYXJJE"
      "&filter=(SECURITY_CODE%3D%22{code}%22)(REPORTDATE%3D%272026-09-30%27)&pageNumber=1&pageSize=3")
U2 = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DMSK_FN_BALANCE"
      "&columns=SECURITY_CODE,DEBT_ASSET_RATIO,CURRENT_RATIO,TOTAL_ASSETS,TOTAL_EQUITY"
      "&filter=(SECURITY_CODE%3D%22{code}%22)(REPORT_DATE%3D%272026-09-30%27)&pageNumber=1&pageSize=3")

def g(u):
    for _ in range(3):
        try:
            r = S.get(u, timeout=20).json()
            if r.get("result") and r["result"]["data"]:
                return r["result"]["data"][0]
        except Exception:
            time.sleep(0.6)
    return {}

codes = ["001267","300302","002217","300102","603881","688208","603005","000062",
         "688388","600577","300660","688006","603906","002531","300409","002245"]

def work(c):
    a = g(U1.format(code=c)); b = g(U2.format(code=c))
    return {"code":c,"name":a.get("SECURITY_NAME_ABBR"),
            "np":a.get("PARENT_NETPROFIT"),"sjltz":a.get("SJLTZ"),
            "ocf_ps":a.get("MGJYXJJE"),"dar":b.get("DEBT_ASSET_RATIO"),
            "cr":b.get("CURRENT_RATIO")}

with ThreadPoolExecutor(max_workers=6) as ex:
    res = list(ex.map(work, codes))

json.dump(res, open("risk.json","w"), ensure_ascii=False)
print(f'{"code":<7}{"name":<8}{"净利(亿)":>10}{"同比%":>10}{"每股现金流":>10}{"资产负债率%":>11}{"流动比":>8}')
for x in res:
    np_ = round(x["np"]/1e8,2) if x["np"] else None
    sj = round(x["sjltz"],1) if isinstance(x["sjltz"],(int,float)) else x["sjltz"]
    print(f'{x["code"]:<7}{x["name"]:<8}{str(np_):>10}{str(sj):>10}{str(x["ocf_ps"]):>10}{str(round(x["dar"],1) if x["dar"] else None):>11}{str(round(x["cr"],2) if x["cr"] else None):>8}')
