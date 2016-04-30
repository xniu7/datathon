
product_hs={'052709':'Crude Petroleum', '147108':'Gold', '168471':'Computers', '168517':'Telephone Sets', '168528':'TV'}

product_sitc={'523330':'Crude Petroleum', '519710':'Gold', '117520':'Computers', '117521':'Computers', '117522':'Computers', '117523':'Computers', '117524':'Computers', '117525':'Computers', '117528':'Computers', '117641':'Telephone Sets', '117610':'TV', '117611':'TV', '117612':'TV'}


def generateShowData(rawData, products):
    show_data = {}
    for year in rawData.keys():
        show_data[year]={}
        current_year = show_data[year]
        id_scores = data[year]
        for (id, score) in id_scores:
            if id not in products.keys(): continue
            if products[id] not in current_year: current_year[products[id]]=0
            current_year[products[id]]+=score
    return show_data


filename="product_results.dat"
f = open(filename, 'r')
for line in f:
    data = eval(line)
    show_data = generateShowData(data, product_hs)
#print show_data
    for year in show_data:
        current_year = show_data[year]
        print year, current_year['Crude Petroleum'], current_year['Gold'], current_year['Computers'], current_year['Telephone Sets'], current_year['TV']
