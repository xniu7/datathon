import json
import urllib2

country = "usa"
year = "2013"
hscode = "hs07"

addr = "http://atlas.media.mit.edu/"+hscode+"/export/"+year+"/"+country+"/all/show/"
response = urllib2.urlopen(addr)
html = response.read()
data = json.loads(html)

export_val = data["data"][0]["export_val"]
import_val = data["data"][0]["import_val"]

print hscode, year, country, import_val, export_val
