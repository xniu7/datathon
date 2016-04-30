import json
import urllib2

country_list = ["ago","bdi","ben","bfa","bwa","caf","civ","cmr","cod","cog","com","cpv","dji","dza","egy","eri","esh","eth","gab","gha","gin","gmb","gnb","gnq","ken","lbr","lby","lso","mar","mdg","mli","moz","mrt","mus","mwi","myt","nam","ner","nga","reu","rwa","sdn","sen","shn","sle","som","ssd","stp","swz","syc","tcd","tgo","tun","tza","uga","zaf","zmb","zwe","ata","atf","bvt","hmd","sgs","afg","are","arm","aze","bgd","bhr","brn","btn","cck","chn","cxr","cyp","geo","hkg","idn","ind","iot","irn","irq","isr","jor","jpn","kaz","kgz","khm","kor","kwt","lao","lbn","lka","mac","mdv","mid","mmr","mng","mys","npl","omn","pak","phl","prk","pse","qat","sau","sgp","syr","tha","tjk","tkm","tls","tur","twn","uzb","vnm","yar","yem","ymd","alb","and","aut","bel","bgr","bih","blr","blx","che","chi","csk","cze","ddr","deu","dnk","esp","est","fdr","fin","fra","fro","gbr","gib","grc","hrv","hun","imn","irl","isl","ita","ksv","lie","ltu","lux","lva","mco","mda","mkd","mlt","mne","nld","nor","pol","prt","rou","rus","scg","sjm","smr","srb","sun","svk","svn","swe","ukr","vat","yug","abw","aia","ant","atg","bes","bhs","blm","blz","bmu","brb","can","cri","cub","cuw","cym","dma","dom","grd","grl","gtm","hnd","hti","jam","kna","lca","maf","mex","msr","mtq","naa","nic","pan","pci","pcz","pri","slv","spm","tca","tto","umi","usa","vct","vgb","vir","asm","aus","cok","fji","fsm","glp","gum","kir","mhl","mnp","ncl","nfk","niu","nru","nzl","pcn","plw","png","pyf","slb","tkl","ton","tuv","vut","wlf","wsm","arg","bol","bra","chl","col","ecu","flk","guf","guy","per","pry","sur","ury","ven"]

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
        if entry[hscode+"_id_len"]!=6.0: continue

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







