import sys

country={'usa':'usa', 'chn':'chn', 'ind':'ind', 'jpn':'jpn', 'deu':'deu', 'gbr':'gbr', 'rus':'rus', 'irq':'irq', 'irn':'irn', 'afg':'afg', 'sau':'sau', 'grc':'grc', 'isl':'isl', 'sun':'rus'}

product_hs={'052709':'Crude Petroleum', '147108':'Gold', '168471':'Computers', '168517':'Telephone Sets', '168528':'TV'}

product_sitc={'523330':'Crude Petroleum', '519710':'Gold', '117520':'Computers', '117521':'Computers', '117522':'Computers', '117523':'Computers', '117524':'Computers', '117525':'Computers', '117528':'Computers', '117641':'Telephone Sets', '117610':'TV', '117611':'TV', '117612':'TV'}


def generateShowData(rawData, products):
    show_data = {}
    for year in rawData.keys():
        show_data[year]={}
        current_year = show_data[year]
        id_scores = data[year]
        
        for product in products.values():
            current_year[product]=0
        for (id, score) in id_scores:
            if id not in products.keys(): continue
            
            current_year[products[id]]+=score/100
    return show_data

filename= sys.argv[1]
f = open(filename, 'r')
for line in f:
    data = eval(line)

    if filename == "recent_product_result.dat" or filename == "old_product_result.dat":
        if filename == "recent_product_result.dat": products = product_hs
        elif filename == "old_product_result.dat": products = product_sitc
        show_data = generateShowData(data, products)
        #print show_data
        for year in show_data:
            current_year = show_data[year]
            print year, current_year['Crude Petroleum'], current_year['Gold'], current_year['Computers'], current_year['Telephone Sets'], current_year['TV']
    else :
        show_data = generateShowData(data, country)
        #print show_data
        for year in show_data:
            current_year = show_data[year]
            print year, current_year['usa'], current_year['chn'], current_year['ind'], current_year['jpn'], current_year['deu'], current_year['gbr'], current_year['rus'], current_year['irq'], current_year['irn'], current_year['afg'], current_year['sau'], current_year['grc'], current_year['isl']






