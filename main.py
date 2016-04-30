import bipartite
import json
import sys

def write_to_csv(scores, name='country_scores.csv'):
    try:
        with open(name, 'w') as fp:
            for k, v in scores:
                fp.writelines("%s, %s\n"%(k, v))
        fp.close()

    except Exception, e:
        print e
        exit()

if __name__ == "__main__":
    try:
        dir = sys.argv[1]
        start_year = int(sys.argv[2])
        end_year = int(sys.argv[3])
    except Exception, e:
        print e
        sys.exit()
    
    # run alg on these countries, if empty, run on all countries
    country_list = \
        ["ago","bdi","ben","bfa","bwa","caf","civ","cmr","cod","cog","com","cpv","dji","dza","egy","eri","esh","eth","gab","gha","gin","gmb","gnb","gnq","ken","lbr","lby","lso","mar","mdg","mli","moz","mrt","mus","mwi","myt","nam","ner","nga","reu","rwa","sdn","sen","shn","sle","som","ssd","stp","swz","syc","tcd","tgo","tun","tza","uga","zaf","zmb","zwe","ata","atf","bvt","hmd","sgs","afg","are","arm","aze","bgd","bhr","brn","btn","cck","chn","cxr","cyp","geo","hkg","idn","ind","iot","irn","irq","isr","jor","jpn","kaz","kgz","khm","kor","kwt","lao","lbn","lka","mac","mdv","mid","mmr","mng","mys","npl","omn","pak","phl","prk","pse","qat","sau","sgp","syr","tha","tjk","tkm","tls","tur","twn","uzb","vnm","yar","yem","ymd","alb","and","aut","bel","bgr","bih","blr","blx","che","chi","csk","cze","ddr","deu","dnk","esp","est","fdr","fin","fra","fro","gbr","gib","grc","hrv","hun","imn","irl","isl","ita","ksv","lie","ltu","lux","lva","mco","mda","mkd","mlt","mne","nld","nor","pol","prt","rou","rus","scg","sjm","smr","srb","sun","svk","svn","swe","ukr","vat","yug","abw","aia","ant","atg","bes","bhs","blm","blz","bmu","brb","can","cri","cub","cuw","cym","dma","dom","grd","grl","gtm","hnd","hti","jam","kna","lca","maf","mex","msr","mtq","naa","nic","pan","pci","pcz","pri","slv","spm","tca","tto","umi","usa","vct","vgb","vir","asm","aus","cok","fji","fsm","glp","gum","kir","mhl","mnp","ncl","nfk","niu","nru","nzl","pcn","plw","png","pyf","slb","tkl","ton","tuv","vut","wlf","wsm","arg","bol","bra","chl","col","ecu","flk","guf","guy","per","pry","sur","ury","ven"]


    # run alg on these products, if empty, run on all products
    product_list = []

    country_rank_year = {}
    product_rank_year = {}
    
    for year in range(start_year, end_year+1):
        print "Started year "+str(year)
        im_ex_file = dir+"/"+str(year)
        import_export_data = bipartite.load_im_ex_data(im_ex_file)
    
        graph = bipartite.build_bipartite_graph(import_export_data, country_list=country_list, product_list=product_list)
    
        country_mapping, product_mapping, country_prod_matrix, prod_country_matrix = bipartite.calc_transition_matrixs(graph)
    
        country_scores, product_scores = bipartite.run_bipartite(country_prod_matrix, prod_country_matrix, max_iter=10000, tol=1.0e-5)
    
        # normalize scores to [0, 100]
        country_scores = bipartite.normalize(country_scores)
        product_scores = bipartite.normalize(product_scores)
    
        country_id_scores = {graph.node[id_]['entity_id']:country_scores[idx] for id_, idx in country_mapping.iteritems()}
        product_id_scores = {graph.node[id_]['entity_id']:product_scores[idx] for id_, idx in product_mapping.iteritems()}
    
        country_id_scores = sorted(country_id_scores.iteritems(), key=lambda d:d[1], reverse=True)
        product_id_scores = sorted(product_id_scores.iteritems(), key=lambda d:d[1], reverse=True)

        country_rank_year[year]=country_id_scores
        product_rank_year[year]=product_id_scores
        if year == 2000: write_to_csv(country_id_scores, "country_scores.csv")


    with open("country_results.dat", 'w') as f:
        f.write(str(country_rank_year))
        f.close()
    with open("product_results.dat", 'w') as f:
        f.write(str(product_rank_year))
        f.close()

