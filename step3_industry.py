import requests, json, time
from concurrent.futures import ThreadPoolExecutor

S = requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
URL = "https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code={code}"

data = json.load(open("with_chg.json"))
pool = [x for x in data if x["chg_6m"] <= -45]
print("待查行业:", len(pool))

def fetch(x):
    code = ("SH" if x["symbol"].startswith("sh") else "SZ") + x["code"]
    for _ in range(3):
        try:
            r = S.get(URL.format(code=code), timeout=20)
            d = r.json()
            names = [b["BOARD_NAME"] for b in d.get("ssbk", [])]
            x["boards"] = names
            # 东财行业层级一般在前3位
            x["industry"] = "|".join(names[:3])
            return x
        except Exception:
            time.sleep(0.8)
    x["boards"] = []; x["industry"] = ""
    return x

out = []
with ThreadPoolExecutor(max_workers=6) as ex:
    for x in ex.map(fetch, pool):
        out.append(x)

json.dump(out, open("with_industry.json","w"), ensure_ascii=False)
for x in sorted(out, key=lambda y: y["chg_6m"]):
    print(f'{x["code"]} {x["name"]:<7} {x["chg_6m"]:>7}% 市值{x["mktcap_yi"]:<7} 现价{x["price"]:<6} | {x["industry"]}')
