import networkx as nx
import sys

users=["ago","bdi","ben","bfa","bwa","caf","civ","cmr","cod","cog","com","cpv","dji","dza","egy","eri","esh","eth","gab","gha","gin","gmb","gnb","gnq","ken","lbr","lby","lso","mar","mdg","mli","moz","mrt","mus","mwi","myt","nam","ner","nga","reu","rwa","sdn","sen","shn","sle","som","ssd","stp","swz","syc","tcd","tgo","tun","tza","uga","zaf","zmb","zwe","ata","atf","bvt","hmd","sgs","afg","are","arm","aze","bgd","bhr","brn","btn","cck","chn","cxr","cyp","geo","hkg","idn","ind","iot","irn","irq","isr","jor","jpn","kaz","kgz","khm","kor","kwt","lao","lbn","lka","mac","mdv","mid","mmr","mng","mys","npl","omn","pak","phl","prk","pse","qat","sau","sgp","syr","tha","tjk","tkm","tls","tur","twn","uzb","vnm","yar","yem","ymd","alb","and","aut","bel","bgr","bih","blr","blx","che","chi","csk","cze","ddr","deu","dnk","esp","est","fdr","fin","fra","fro","gbr","gib","grc","hrv","hun","imn","irl","isl","ita","ksv","lie","ltu","lux","lva","mco","mda","mkd","mlt","mne","nld","nor","pol","prt","rou","rus","scg","sjm","smr","srb","sun","svk","svn","swe","ukr","vat","yug","abw","aia","ant","atg","bes","bhs","blm","blz","bmu","brb","can","cri","cub","cuw","cym","dma","dom","grd","grl","gtm","hnd","hti","jam","kna","lca","maf","mex","msr","mtq","naa","nic","pan","pci","pcz","pri","slv","spm","tca","tto","umi","usa","vct","vgb","vir","asm","aus","cok","fji","fsm","glp","gum","kir","mhl","mnp","ncl","nfk","niu","nru","nzl","pcn","plw","png","pyf","slb","tkl","ton","tuv","vut","wlf","wsm","arg","bol","bra","chl","col","ecu","flk","guf","guy","per","pry","sur","ury","ven"]

users = ['chn','usa','ind', 'jpn', 'deu', 'gbr', 'rus']

def loadData(filename):
    f = open(filename, 'r')
    for line in f:
        data = eval(line)
        return data

def createBipart():
    BG = nx.DiGraph()
    BG.add_edge('ind','i1',weight=4.0)
    BG.add_edge('ind','i2',weight=1.0)
    BG.add_edge('chn','i2',weight=2.0)
    BG.add_edge('usa','i2',weight=1.0)
    
    BG.add_edge('i1','ind',weight=3.0)
    BG.add_edge('i1','chn',weight=1.0)
    BG.add_edge('i2','chn',weight=1.0)
    BG.add_edge('i2','usa',weight=3.0)
    return BG
'''
def createBipart(data):
    BG = nx.DiGraph()
    for country in data.keys():
        products = data[country]
        for product in products:
            BG.add_edge(country,product['id'],weight=product['import'])
            BG.add_edge(product['id'],country,weight=product['export'])

    return BG
'''
def bipart2graph(BG, users):
    G=nx.DiGraph()
    for user in users:
        if user not in BG.nodes(): continue
        user_weight = 0
        for item in BG.neighbors(user):
            user_weight+=BG[user][item]['weight']
        if user_weight ==0 : continue
        for item in BG.neighbors(user):
            item_weight = 0
            for user2 in BG.neighbors(item):
                if user2 not in users: continue
                item_weight+=BG[item][user2]['weight']
            if item_weight ==0 : continue
            for user2 in BG.neighbors(item):
                if user2 not in users: continue
                if (user, user2) not in G.edges(): G.add_edge(user,user2,weight=0)
                G[user][user2]['weight']+=BG[user][item]['weight']*BG[item][user2]['weight']/user_weight/item_weight
    return G

#data = loadData(sys.argv[1])
BG = createBipart()
G = bipart2graph(BG, users)
print G.edges()
pr = nx.pagerank(G, alpha=0.9)

print pr['ind']*3, pr['chn']*3, pr['usa']*3