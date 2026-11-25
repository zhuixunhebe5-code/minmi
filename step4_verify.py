import requests, json, time
S = requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0","Referer":"https://finance.sina.com.cn"})
URL=("https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData"
     "?symbol={sym}&scale=240&ma=no&datalen=250")
codes=["sh603063","sz001267","sz300302","sz300323","sz002217","sh601615","sh688388",
       "sz300131","sh600589","sh600330","sz000547","sh688709","sz300762","sz300102",
       "sh603881","sh688208","sh603005","sz300166","sh688055","sz002491","sz300113",
       "sh600850","sz300077","sh600745","sz002413","sz300184"]
for sym in codes:
    try:
        k=json.loads(S.get(URL.format(sym=sym),timeout=20).text.replace("'",'"'))
        cl=[(r["day"],float(r["close"])) for r in k]
        gaps=[(cl[i][0],round((cl[i][1]/cl[i-1][1]-1)*100,1)) for i in range(1,len(cl)) if abs(cl[i][1]/cl[i-1][1]-1)>0.15]
        print(sym, "天数",len(cl), "首",cl[0][0],cl[0][1],"末",cl[-1][0],cl[-1][1], "异常跳空",gaps[:3])
    except Exception as e:
        print(sym,"ERR",e)
    time.sleep(0.3)
