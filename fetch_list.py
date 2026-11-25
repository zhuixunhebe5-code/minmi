import requests, json, time
s = requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0","Referer":"https://finance.sina.com.cn"})
# total count
try:
    r = s.get("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeStockCount?node=hs_a", timeout=20)
    print("count resp:", r.text[:100])
except Exception as e:
    print("count err", e)
