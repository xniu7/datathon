import json
import urllib2

country_list = ["AFG","ALA","ALB","DZA","ASM","AND","AGO","AIA","ATG","ARG","ARM","ABW","AUS","AUT","AZE","BHS","BHR","BGD","BRB","BLR","BEL","BLZ","BEN","BMU","BTN","BOL","BIH","BWA","BRA","VGB","BRN","BGR","BFA","BDI","KHM","CMR","CAN","CPV","CYM","CAF","TCD","CHL","CHN","HKG","MAC","COL","COM","COG","COK","CRI","CIV","HRV","CUB","CYP","CZE","PRK","COD","DNK","DJI","DMA","DOM","ECU","EGY","SLV","GNQ","ERI","EST","ETH","FRO","FLK","FJI","FIN","FRA","GUF","PYF","GAB","GMB","GEO","DEU","GHA","GIB","GRC","GRL","GRD","GLP","GUM","GTM","GGY","GIN","GNB","GUY","HTI","VAT","HND","HUN","ISL","IND","IDN","IRN","IRQ","IRL","IMN","ISR","ITA","JAM","JPN","JEY","JOR","KAZ","KEN","KIR","KWT","KGZ","LAO","LVA","LBN","LSO","LBR","LBY","LIE","LTU","LUX","MDG","MWI","MYS","MDV","MLI","MLT","MHL","MTQ","MRT","MUS","MYT","MEX","FSM","MDA","MCO","MNG","MNE","MSR","MAR","MOZ","MMR","NAM","NRU","NPL","NLD","ANT","NCL","NZL","NIC","NER","NGA","NIU","NFK","MNP","NOR","PSE","OMN","PAK","PLW","PAN","PNG","PRY","PER","PHL","PCN","POL","PRT","PRI","QAT","KOR","REU","ROU","RUS","RWA","BLM","SHN","KNA","LCA","MAF","SPM","VCT","WSM","SMR","STP","SAU","SEN","SRB","SYC","SLE","SGP","SVK","SVN","SLB","SOM","ZAF","ESP","LKA","SDN","SUR","SJM","SWZ","SWE","CHE","SYR","TJK","THA","MKD","TLS","TGO","TKL","TON","TTO","TUN","TUR","TKM","TCA","TUV","UGA","UKR","ARE","GBR","TZA","USA","VIR","URY","UZB","VUT","VEN","VNM","WLF","ESH","YEM","ZMB","ZWE"]

def getCountryData(country, year, hscode):
    addr = "http://atlas.media.mit.edu/"+hscode+"/export/"+year+"/"+country+"/all/show/"
    country_data=[]

    try:
        response = urllib2.urlopen(addr)
        html = response.read()
    except urllib2.HTTPError:
        print country
        return country_data

    country_raw_data = json.loads(html)

    if "data" not in country_raw_data.keys(): return country_data
    
    for entry in country_raw_data["data"]:
        product = {}
        product_id = entry[hscode+"_id"]

        if "export_val" not in entry.keys():
            export_val = 0
        else : export_val = entry["export_val"]
        if "import_val" not in entry.keys():
            import_val = 0
        else : import_val = entry["import_val"]
        product["id"] = product_id
        product["import"] = import_val
        product["export"] = export_val
        country_data.append(product)
    return country_data

def getAllCountries(year, hscode):
    data = {}
    for country in country_list:
        country_data = getCountryData(country, year, hscode)
        if country_data:
            data[country] = country_data
    return data


year = "2013"
hscode = "hs07"
data = getAllCountries(year, hscode)

target = open('data', 'w')
target.write(str(data))
target.close()







