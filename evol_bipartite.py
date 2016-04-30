import networkx as nx
import numpy as np
import sys

# G_copy.add_nodes_from(G.nodes(data=True))


class EvolBipartite:
    def __init__(self):
        self.country_ids = {} # country id - graph id mapping
        self.product_ids = {} # product id - graph id mapping
        self.country_list = [] # country list
        self.product_list = [] # product list
        self.country_mapping = {} # country graph_id - idx mapping
        self.product_mapping = {} # product graph_id - idx mapping
        self.n_countries = 0
        self.n_products = 0




    def update_bipartite_graph(self, graph, import_export_data):
        new_graph = nx.DiGraph()

        # use nodes in original graph
        new_graph.add_nodes_from(graph.nodes(data=True))

        # add new edges
        # add country - product edges
        for country, records in import_export_data.iteritems():
            if not country in self.country_list:
                continue

            for each_record in records:
                if not each_record['id'] in self.product_list:
                    continue

                if not each_record['import'] == 0:
                    new_graph.add_edge(self.country_ids[country], self.product_ids[each_record['id']], weight=each_record['import']) # import edge

                if not each_record['export'] == 0:
                    new_graph.add_edge(self.product_ids[each_record['id']], self.country_ids[country], weight=each_record['export']) # export edge


        # create a copy in (right) stochastic form
        W = nx.stochastic_graph(new_graph, weight='weight')

        return W


    def build_bipartite_graph(self, country_list, product_list):
        self.country_list = country_list
        self.product_list = product_list


        graph = nx.DiGraph()
        next_id = 0

        print "loading %s countries and %s products..." % (len(self.country_list), len(self.product_list))


        # add country nodes
        for country in self.country_list:
            graph.add_node(next_id,
                        type="country",
                        entity_id=country
                        )

            self.country_ids[country] = next_id
            next_id += 1


        # add country nodes
        for product in self.product_list:
            graph.add_node(next_id,
                        type="product",
                        entity_id=product
                        )

            self.product_ids[product] = next_id
            next_id += 1


        # we use graph ids internally
        countries = [u for u in graph.nodes() if graph.node[u]["type"] == "country"]
        products = [u for u in graph.nodes() if graph.node[u]["type"] == "product"]

        self.n_countries = len(countries)
        self.n_products = len(products)


        # graph_id - idx mapping
        self.country_mapping = dict(zip(countries, range(self.n_countries)))
        self.product_mapping = dict(zip(products, range(self.n_products)))


        return graph



    def calc_transition_matrixs(self, graph):

        country_prod_matrix = np.zeros((self.n_countries, self.n_products))
        prod_country_matrix = np.zeros((self.n_products, self.n_countries))


        # compute country_prod_matrix (imports)
        for each_country in countries:
            for each_product in graph[each_country]:
                country_prod_matrix[self.country_mapping[each_country]][self.product_mapping[each_product]] \
                                    = graph[each_country][each_product]['weight']


        # compute prod_country_matrix (exports)
        for each_product in products:
            for each_country in graph[each_product]:
                prod_country_matrix[self.product_mapping[each_product]][self.country_mapping[each_country]] \
                                    = graph[each_product][each_country]['weight']



        # handle "dangling" nodes
        # "dangling" nodes only consume energies, so we release these energies manually
        country_norm = np.sum(country_prod_matrix, 1)
        for i in range(self.n_countries):
            if country_norm[i] == 0:
                country_prod_matrix[i] = 1.0 / self.n_products


        product_norm = np.sum(prod_country_matrix, 1)
        for i in range(self.n_products):
            if product_norm[i] == 0:
                prod_country_matrix[i] = 1.0 / self.n_countries


        return country_prod_matrix, prod_country_matrix



    def calc_cum_transition_matrix(self, country_prod_matrix_list):
        """
        compute cumulative transition matrices given a list of country_prod_matrix and prod_country_matrix.
        """

        cum_country_country_matrix = np.identity(self.n_countries)
        for country_prod_matrix, prod_country_matrix in country_prod_matrix_list[:-1]:
            cum_country_country_matrix = cum_country_country_matrix.dot(country_prod_matrix).dot(prod_country_matrix)


        cum_country_prod_matrix = cum_country_country_matrix.dot(country_prod_matrix_list[-1][0])
        cum_country_country_matrix = cum_country_prod_matrix.dot(country_prod_matrix_list[-1][1])

        return cum_country_country_matrix, cum_country_prod_matrix




    def run_bipartite(self, cum_country_country_matrix, cum_country_prod_matrix, max_iter=1000, tol=1.0e-8):
        """
        run bipartite alg
        """

        country_scores = np.ones((n_countries, ))
        product_scores = np.ones((n_products, ))


        # propogation on a bipartite network
        # power iteration: make up to max_iter iterations
        # set country_scores as convergence condition
        itr = 0
        while True:
            country_scores_last = country_scores

            # country to country
            country_scores = country_scores.dot(cum_country_country_matrix)


            # check convergence, l1 norm
            err = np.linalg.norm(country_scores - country_scores_last, 1)

            if err < tol:
                print "converged in %d iterations." % itr
                break

            if itr > max_iter:
                raise Exception('pagerank: power iteration failed to converge '
                                                            'in %d iterations.'%(itr-1))
            itr += 1


        # update product_scores
        product_scores = country_scores.dot(cum_country_prod_matrix)

        return country_scores, product_scores



def load_all_data(file_list):
    data_list = []
    for in_file in file_list:
        data_list.append(load_im_ex_data(in_file))

    return data_list


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


def write_to_csv(scores, name='country_scores.csv'):

    try:
        with open(name, 'w') as fp:
            for k, v in scores:
                fp.writelines("%s, %s\n"%(k, v))

    except Exception, e:
        print e
        exit()


def normalize(x, range_=100.0, method='linear'):
    if method == 'linear':
        max_, min_ = np.max(x), np.min(x)
        return (x - min_) * range_ / (max_ - min_) if not max_ == min_ else range_ * x / max_
    elif method == 'log':
        pass
    else:
        print "invalid argument method: %s" % method
        exit()


if __name__ == "__main__":
    try:
        file_list = sys.argv[1:]
    except Exception, e:
        print e
        sys.exit()

    # run alg on these countries, if empty, run on all countries
    country_list = sys.argv[2] if 2 in sys.argv else \
            ["ago","bdi","ben","bfa","bwa","caf","civ","cmr","cod","cog","com","cpv","dji","dza","egy","eri","esh","eth","gab","gha","gin","gmb","gnb","gnq","ken","lbr","lby","lso","mar","mdg","mli","moz","mrt","mus","mwi","myt","nam","ner","nga","reu","rwa","sdn","sen","shn","sle","som","ssd","stp","swz","syc","tcd","tgo","tun","tza","uga","zaf","zmb","zwe","ata","atf","bvt","hmd","sgs","afg","are","arm","aze","bgd","bhr","brn","btn","cck","chn","cxr","cyp","geo","hkg","idn","ind","iot","irn","irq","isr","jor","jpn","kaz","kgz","khm","kor","kwt","lao","lbn","lka","mac","mdv","mid","mmr","mng","mys","npl","omn","pak","phl","prk","pse","qat","sau","sgp","syr","tha","tjk","tkm","tls","tur","twn","uzb","vnm","yar","yem","ymd","alb","and","aut","bel","bgr","bih","blr","blx","che","chi","csk","cze","ddr","deu","dnk","esp","est","fdr","fin","fra","fro","gbr","gib","grc","hrv","hun","imn","irl","isl","ita","ksv","lie","ltu","lux","lva","mco","mda","mkd","mlt","mne","nld","nor","pol","prt","rou","rus","scg","sjm","smr","srb","sun","svk","svn","swe","ukr","vat","yug","abw","aia","ant","atg","bes","bhs","blm","blz","bmu","brb","can","cri","cub","cuw","cym","dma","dom","grd","grl","gtm","hnd","hti","jam","kna","lca","maf","mex","msr","mtq","naa","nic","pan","pci","pcz","pri","slv","spm","tca","tto","umi","usa","vct","vgb","vir","asm","aus","cok","fji","fsm","glp","gum","kir","mhl","mnp","ncl","nfk","niu","nru","nzl","pcn","plw","png","pyf","slb","tkl","ton","tuv","vut","wlf","wsm","arg","bol","bra","chl","col","ecu","flk","guf","guy","per","pry","sur","ury","ven"]


    # run alg on these products, if empty, run on all products
    # product_list = sys.argv[3] if 3 in sys.argv else [u'15720890', u'13681091', u'18920590', u'16845910']
    product_list = []

    # load all data
    file_list = []
    data_list = load_all_data(file_list)

    eBip = EvolBipartite()

    graph = eBip.build_bipartite_graph(country_list, product_list)


    country_prod_matrix_list = []
    for import_export_data in data_list:
        graph = eBip.update_bipartite_graph(graph, import_export_data)

        country_prod_matrix, prod_country_matrix = eBip.calc_transition_matrixs(graph)
        country_prod_matrix_list.append((country_prod_matrix, prod_country_matrix))



    print "###########"
    print "summary"
    print "###########"


    for idx in range(1, len(data_list) + 1):
        cum_country_country_matrix, cum_country_prod_matrix = \
                    eBip.calc_cum_transition_matrix(country_prod_matrix_list[:idx])

        country_scores, product_scores = eBip.run_bipartite(cum_country_country_matrix, cum_country_prod_matrix, max_iter=10000, tol=1.0e-5)

        # normalize scores to [0, 100]
        country_scores = normalize(country_scores)
        product_scores = normalize(product_scores)

        country_id_scores = {graph.node[id_]['entity_id']:country_scores[idx] for id_, idx in eBip.country_mapping.iteritems()}
        product_id_scores = {graph.node[id_]['entity_id']:product_scores[idx] for id_, idx in eBip.product_mapping.iteritems()}

        country_id_scores = sorted(country_id_scores.iteritems(), key=lambda d:d[1], reverse=True)
        product_id_scores = sorted(product_id_scores.iteritems(), key=lambda d:d[1], reverse=True)


        # write to csv
        write_to_csv(country_id_scores, "country_scores_%s.csv"%idx)
        write_to_csv(product_id_scores, "product_scores_%s.csv"%idx)


        print "\n Ranking based on the records from the Year 1 to Year %s:" % idx
        print "\ntop 10 countries"
        for id_, score in country_id_scores[:10]:
            print "%s: %s" % (id_, round(score, 1))

        print "\ntop 10 products"
        for id_, score in product_id_scores[:10]:
            print "%s: %s" % (id_, round(score, 1))


