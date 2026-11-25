import requests, json, time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

S = requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                  "Referer":"https://finance.sina.com.cn"})
URL = ("https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData"
       "?symbol={sym}&scale=240&ma=no&datalen=250")

cand = json.load(open("cand.json"))

def get(c):
    for _ in range(3):
        try:
            r = S.get(URL.format(sym=c["symbol"]), timeout=25)
            t = r.text.strip()
            if not t.startswith("["): 
                time.sleep(0.6); continue
            k = json.loads(t.replace("'", '"'))
            if not k: 
                time.sleep(0.6); continue
            return c, k
        except Exception:
            time.sleep(0.8)
    return c, None

out = []
done = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    for c, k in ex.map(get, cand):
        done += 1
        if not k or len(k) < 30: continue
        closes = [(row["day"], float(row["close"])) for row in k]
        last_day, last_close = closes[-1]
        # 目标起点：半年前 2026-05-25 附近
        tgt = "2026-05-25"
        before = [x for x in closes if x[0] <= tgt]
        if not before: continue
        start_day, start_close = before[-1]
        if start_close <= 0: continue
        chg = (last_close/start_close - 1)*100
        c2 = dict(c)
        c2.update({"last_day":last_day,"last_close":round(last_close,2),
                   "start_day":start_day,"start_close":round(start_close,2),
                   "chg_6m":round(chg,2)})
        out.append(c2)
        if done % 100 == 0: print("progress", done)

print("valid:", len(out))
json.dump(out, open("with_chg.json","w"), ensure_ascii=False)
srt = sorted(out, key=lambda x:x["chg_6m"])
print("跌幅前15:")
for x in srt[:15]:
    print(f'{x["symbol"]} {x["name"]:<8} 现价{x["price"]:<7} 市值{x["mktcap_yi"]:<8} 半年{x["chg_6m"]:>7}%  {x["start_day"]}->{x["last_day"]}')
print("跌幅>50%数量:", sum(1 for x in out if x["chg_6m"]<=-50))
print("跌幅45-75%数量:", sum(1 for x in out if -75<=x["chg_6m"]<=-45))
