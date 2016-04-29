import networkx as nx
import numpy as np
import sys


def build_bipartite_graph(import_export_data, country_list=[], product_list=[]):
    """
    If country_list and product_list are not empty, then
    we only care about countries and products in the lists.
    """


    graph = nx.DiGraph()

    country_ids = {}
    product_ids = {}

    next_id = 0

    countries = set(import_export_data.keys())
    products = set([y['id'] for x in import_export_data.values() for y in x])

    filtered_countries = countries & set(country_list) if country_list else countries
    filtered_products = products & set(product_list) if product_list else products

    print "loading %s countries and %s products..." % (len(filtered_countries), len(filtered_products))


    # add country nodes
    for country in filtered_countries:
        graph.add_node(next_id,
                    type="country",
                    entity_id=country
                    )

        country_ids[country] = next_id
        next_id += 1


    # add country nodes
    for product in filtered_products:
        graph.add_node(next_id,
                    type="product",
                    entity_id=product
                    )

        product_ids[product] = next_id
        next_id += 1



    # add country - product edges
    for country, records in import_export_data.iteritems():
        if not country in filtered_countries:
            continue

        for each_record in records:
            if not each_record['id'] in filtered_products:
                continue

            if not each_record['import'] == 0:
                graph.add_edge(country_ids[country], product_ids[each_record['id']], weight=each_record['import']) # import edge

            if not each_record['export'] == 0:
                graph.add_edge(product_ids[each_record['id']], country_ids[country], weight=each_record['export']) # export edge



    # create a copy in (right) stochastic form
    W = nx.stochastic_graph(graph, weight='weight')

    return W



def calc_transition_matrixs(graph):

    # we use graph ids internally

    countries = [u for u in graph.nodes() if graph.node[u]["type"] == "country"]
    products = [u for u in graph.nodes() if graph.node[u]["type"] == "product"]

    n_countries = len(countries)
    n_products = len(products)


    # graph_id - idx mapping
    country_mapping = dict(zip(countries, range(n_countries)))
    product_mapping = dict(zip(products, range(n_products)))


    country_prod_matrix = np.zeros((n_countries, n_products))
    prod_country_matrix = np.zeros((n_products, n_countries))


    # compute country_prod_matrix (imports)
    for each_country in countries:
        for each_product in graph[each_country]:
            country_prod_matrix[country_mapping[each_country]][product_mapping[each_product]] \
                                = graph[each_country][each_product]['weight']


    # compute prod_country_matrix (exports)
    for each_product in products:
        for each_country in graph[each_product]:
            prod_country_matrix[product_mapping[each_product]][country_mapping[each_country]] \
                                = graph[each_product][each_country]['weight']


    return country_mapping, product_mapping, country_prod_matrix, prod_country_matrix



def run_bipartite(country_prod_matrix, prod_country_matrix, max_iter=100, tol=1.0e-8):
    """
    run bipartite alg
    """
    n_countries, n_products = country_prod_matrix.shape
    country_scores = np.ones((n_countries, ))
    product_scores = np.ones((n_products, ))

    import pdb;pdb.set_trace()
    # power iteration: make up to max_iter iterations
    # set country_scores as convergence condition
    itr = 0
    while True:
        country_scores_last = country_scores
        product_scores_last = product_scores

        # propogation on a bipartite network


        # 1) country to product
        product_scores = country_scores.dot(country_prod_matrix)

        # 2) product to country
        country_scores = product_scores.dot(prod_country_matrix)


        # check convergence, l1 norm
        err = np.linalg.norm(country_scores - country_scores_last, 1)

        if err < tol:
            print "converged in %d iterations." % itr
            break

        if itr > max_iter:
            raise Exception('pagerank: power iteration failed to converge '
                                                        'in %d iterations.'%(itr-1))
        itr += 1


    return country_scores, product_scores


def load_im_ex_data(in_file):

    try:
        with open(in_file, 'r') as fp:
            data = []
            for line in fp:
                data.append(eval(line))

            if data:
                return data[0]
            else:
                print "no data in the file!"
                exit()

    except Exception, e:
        print e
        exit()


if __name__ == "__main__":
    try:
        im_ex_file = sys.argv[1]
    except Exception, e:
        print e
        sys.exit()

    # run alg on these countries, if empty, run on all countries
    #country_list = sys.argv[2] if 2 in sys.argv else ['usa', 'gbr', 'chn', 'prk', 'irq']
    country_list = ["ago","bdi","ben","bfa","bwa","caf","civ","cmr","cod","cog","com","cpv","dji","dza","egy","eri","esh","eth","gab","gha","gin","gmb","gnb","gnq","ken","lbr","lby","lso","mar","mdg","mli","moz","mrt","mus","mwi","myt","nam","ner","nga","reu","rwa","sdn","sen","shn","sle","som","ssd","stp","swz","syc","tcd","tgo","tun","tza","uga","zaf","zmb","zwe","ata","atf","bvt","hmd","sgs","afg","are","arm","aze","bgd","bhr","brn","btn","cck","chn","cxr","cyp","geo","hkg","idn","ind","iot","irn","irq","isr","jor","jpn","kaz","kgz","khm","kor","kwt","lao","lbn","lka","mac","mdv","mid","mmr","mng","mys","npl","omn","pak","phl","prk","pse","qat","sau","sgp","syr","tha","tjk","tkm","tls","tur","twn","uzb","vnm","yar","yem","ymd","alb","and","aut","bel","bgr","bih","blr","blx","che","chi","csk","cze","ddr","deu","dnk","esp","est","fdr","fin","fra","fro","gbr","gib","grc","hrv","hun","imn","irl","isl","ita","ksv","lie","ltu","lux","lva","mco","mda","mkd","mlt","mne","nld","nor","pol","prt","rou","rus","scg","sjm","smr","srb","sun","svk","svn","swe","ukr","vat","yug","abw","aia","ant","atg","bes","bhs","blm","blz","bmu","brb","can","cri","cub","cuw","cym","dma","dom","grd","grl","gtm","hnd","hti","jam","kna","lca","maf","mex","msr","mtq","naa","nic","pan","pci","pcz","pri","slv","spm","tca","tto","umi","usa","vct","vgb","vir","asm","aus","cok","fji","fsm","glp","gum","kir","mhl","mnp","ncl","nfk","niu","nru","nzl","pcn","plw","png","pyf","slb","tkl","ton","tuv","vut","wlf","wsm","arg","bol","bra","chl","col","ecu","flk","guf","guy","per","pry","sur","ury","ven"]
    # run alg on these products, if empty, run on all products
    # product_list = sys.argv[3] if 3 in sys.argv else [u'15720890', u'13681091', u'18920590', u'16845910']
    product_list = []

    import_export_data = load_im_ex_data(im_ex_file)

    graph = build_bipartite_graph(import_export_data, country_list=country_list, product_list=product_list)

    country_mapping, product_mapping, country_prod_matrix, prod_country_matrix = calc_transition_matrixs(graph)

    country_scores, product_scores = run_bipartite(country_prod_matrix, prod_country_matrix, max_iter=10000, tol=1.0e-5)

    import pdb;pdb.set_trace()
    country_id_scores = {graph.node[id_]['entity_id']:country_scores[idx] for id_, idx in country_mapping.iteritems()}
    product_id_scores = {graph.node[id_]['entity_id']:product_scores[idx] for id_, idx in product_mapping.iteritems()}

    country_id_scores = sorted(country_id_scores.iteritems(), key=lambda d:d[1], reverse=True)
    product_id_scores = sorted(product_id_scores.iteritems(), key=lambda d:d[1], reverse=True)


    print "###########"
    print "summary"
    print "###########"

    print "\ntop 10 countries"
    for id_, score in country_id_scores[:10]:
        print "%s: %s" % (id_, score)

    print "\ntop 10 products"
    for id_, score in product_id_scores[:10]:
        print "%s: %s" % (id_, score)



    # product list: tobacoo 240399, potato 071420, liqing 271320, clothes 620192


    # country list: USA, GBR, CHN, PRK, IRQ




