import requests, json, time
from concurrent.futures import ThreadPoolExecutor

S = requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                  "Referer":"https://finance.sina.com.cn"})
BASE = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
        "Market_Center.getHQNodeData?page={p}&num=100&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=page")

def get(p):
    for _ in range(3):
        try:
            r = S.get(BASE.format(p=p), timeout=25)
            t = r.text.strip()
            if t.startswith("["):
                return json.loads(t)
            # sina sometimes returns js array with single quotes
            return json.loads(t.replace("'", '"'))
        except Exception:
            time.sleep(1)
    return []

rows = []
with ThreadPoolExecutor(max_workers=6) as ex:
    for res in ex.map(get, range(1, 57)):
        rows.extend(res)

print("total fetched:", len(rows))
# 只保留沪深（sh/sz）
hs = [x for x in rows if x["symbol"][:2] in ("sh","sz")]
print("sh+sz:", len(hs))
cand = []
for x in hs:
    try:
        price = float(x["trade"]); mc = float(x["mktcap"])/10000.0  # 亿元
    except: continue
    if price>0 and price<20 and 80<=mc<=200:
        cand.append({"symbol":x["symbol"],"code":x["code"],"name":x["name"],
                     "price":price,"mktcap_yi":round(mc,2),"pe":x.get("per"),"pb":x.get("pb")})
print("price<20 & 80-200亿:", len(cand))
json.dump(cand, open("cand.json","w"), ensure_ascii=False)
for c in cand[:10]: print(c)
