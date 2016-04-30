import networkx as nx
import numpy as np
import sys
import os

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


        # add product nodes
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

        countries = [u for u in graph.nodes() if graph.node[u]["type"] == "country"]
        products = [u for u in graph.nodes() if graph.node[u]["type"] == "product"]

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


    '''
    def calc_cum_transition_matrix(self, country_prod_matrix_list):
        """
        compute cumulative transition matrices given a list of country_prod_matrix and prod_country_matrix.
        """

        cum_country_country_matrix = np.identity(self.n_countries)
        for country_prod_matrix, prod_country_matrix in country_prod_matrix_list[:-1]:
            cc = country_prod_matrix.dot(prod_country_matrix)
            n_cc = cc
            cum_country_country_matrix.dot(ncc)
            cum_country_country_matrix = cum_country_country_matrix.dot(country_prod_matrix).dot(prod_country_matrix)


        cum_country_prod_matrix = cum_country_country_matrix.dot(country_prod_matrix_list[-1][0])
        cum_country_country_matrix = cum_country_prod_matrix.dot(country_prod_matrix_list[-1][1])


        # make stochastic column matrices
        cum_country_country_matrix = self.make_column_stochastic_matrix(cum_country_country_matrix)
        cum_country_prod_matrix = self.make_column_stochastic_matrix(cum_country_prod_matrix)


        return cum_country_country_matrix, cum_country_prod_matrix
    '''
            
    def calc_cum_transition_matrix(self, country_prod_matrix_list):
        """
        compute cumulative transition matrices given a list of country_prod_matrix and prod_country_matrix.
        """
        alpha = 0.9
        country_country_matrix_list = []
        for country_prod_matrix, prod_country_matrix in country_prod_matrix_list[:]:
            country_country_matrix = country_prod_matrix.dot(prod_country_matrix)
            country_country_matrix_list.append(country_country_matrix)
        
        cum_country_country_matrix = np.identity(self.n_countries)
        for country_country_matrix in country_country_matrix_list:
            country_country_matrix = alpha*np.identity(self.n_countries)+(1-alpha)*country_country_matrix
            cum_country_country_matrix=cum_country_country_matrix.dot(country_country_matrix)
        '''
        cum_country_country_matrix = np.zeros((self.n_countries, self.n_countries))
        for country_country_matrix in country_country_matrix_list:
            cum_country_country_matrix += country_country_matrix
        
        row_sums = cum_country_country_matrix.sum(axis=1)
        cum_country_country_matrix /= row_sums[:, np.newaxis]
        '''
        return cum_country_country_matrix, country_prod_matrix



    def run_bipartite(self, cum_country_country_matrix, cum_country_prod_matrix, max_iter=1000, tol=1.0e-8):
        """
        run bipartite alg
        """

        country_scores = np.ones((self.n_countries, ))
        product_scores = np.ones((self.n_products, ))


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





    def from_transition_to_matrix(self, transition_matrix):
        graph = nx.DiGraph()

        # add country nodes
        for country in self.country_list:
            graph.add_node(self.country_ids[country],
                        type="country",
                        entity_id=country
                        )

        # add country - country edges
        for graph_id, idx in self.country_mapping.iteritems():
            for graph_id2, idx2 in self.country_mapping.iteritems():
                if transition_matrix[idx][idx2] > 0:
                    graph.add_edge(graph_id, graph_id2, weight=transition_matrix[idx][idx2])

        return graph


    def run_pagerank(self, G, alpha=0.85, pers=None, max_iter=1000,
                             tol=1.0e-6, nstart=None, weight='weight', node_types=None):
        """Return the PageRank of the nodes in the graph.

        PageRank computes a ranking of the nodes in the graph G based on
        the structure of the incoming links. It was originally designed as
        an algorithm to rank web pages.

        Parameters
        -----------
        G : graph
            A NetworkX graph

        alpha : float, optional
            Damping parameter for PageRank, default=0.85

        pers: dict, optional
             The "pers vector" consisting of a dictionary with a
             key for every graph node and nonzero pers value for each node.

        max_iter : integer, optional
            Maximum number of iterations in power method eigenvalue solver.

        tol : float, optional
            Error tolerance used to check convergence in power method solver.

        nstart : dictionary, optional
            Starting value of PageRank iteration for each node.

        weight : key, optional
            Edge data key to use as weight. If None weights are set to 1.

        Returns
        -------
        pagerank : dictionary
             Dictionary of nodes with PageRank as value

        Notes
        -----
        The eigenvector calculation is done by the power iteration method
        and has no guarantee of convergence.    The iteration will stop
        after max_iter iterations or an error tolerance of
        number_of_nodes(G)*tol has been reached.
        """

        if len(G) == 0:
                return {}

        # create a copy in (right) stochastic form
        W = nx.stochastic_graph(G, weight=weight)

        scale = 1.0 / W.number_of_nodes()

        # choose fixed starting vector if not given
        if nstart is None:
            x = dict.fromkeys(W, scale)
        else:
            x = nstart
            # normalize starting vector to 1
            s = 1.0/sum(x.values())
            for k in x: x[k]*=s

        # assign uniform pers vector if not given
        if pers is None:
            pers = dict.fromkeys(W, scale)
        else:
            # Normalize the sum to 1
            s = sum(pers.values())

            for k in pers.keys():
                pers[k] /= s

            if len(pers)!=len(G):
                    raise Exception('Personalization vector must have a value for every node')


        # "dangling" nodes, no links out from them
        out_degree = W.out_degree()
        dangle = [n for n in W if out_degree[n]==0.0]

        itr = 0
        while True: # power iteration: make up to max_iter iterations
            xlast = x
            x = dict.fromkeys(xlast.keys(), 0)

            # "dangling" nodes only consume energies, so we release these energies manually
            danglesum = alpha*scale*sum(xlast[n] for n in dangle)
            # danglesum = 0

            for n in x:
                # this matrix multiply looks odd because it is
                # doing a left multiply x^T=xlast^T*W
                for nbr in W[n]:
                    x[nbr] += alpha*xlast[n]*W[n][nbr][weight]

                x[n] += danglesum + (1 - alpha) * pers[n]

            # normalize vector
            s = 1.0 / sum(x.values())
            for n in x:
                x[n]*=s


            # check convergence, l1 norm
            err = sum([abs(x[n] - xlast[n]) for n in x])
            if err < tol:
                print "converged in %d iterations." % itr
                break
            if itr > max_iter:
                raise Exception('pagerank: power iteration failed to converge '
                                                        'in %d iterations.'%(itr-1))
            itr += 1



        # Returns:
        #   x: PageRank of each node;
        #   l: Detailed contributions of each layer;
        #   itr: Iterations to converge.

        return x, itr





    def make_column_stochastic_matrix(self, matrix):
        n_rows, _ = matrix.shape

        sum_ = np.sum(matrix, 1)
        for i in range(n_rows):
            if sum_[i] != 1:
                matrix[i] = matrix[i] / sum_[i]

        return matrix




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


def normalize2(x, range_=100.0, method='linear'):
    if method == 'linear':
        max_, min_ = np.max(x), np.min(x)
        return (x - min_) * range_ / (max_ - min_) if not max_ == min_ else range_ * x / max_
    elif method == 'log':
        pass
    else:
        print "invalid argument method: %s" % method
        exit()



def normalize(x):
    sum = np.sum(x)

    return x*100/sum






if __name__ == "__main__":

    path = "results/cum"
    if not os.path.exists(path):
        os.makedirs(path)


    if len(sys.argv) > 1:
        file_list = sys.argv[1:]
    else:
        data_root = "../data/cum"

        years = range(1962, 2015)
        file_list = ["%s/%s"%(data_root, y) for y in years]


    print "# of data files: %s" % len(file_list)




    # load all data
    data_list = load_all_data(file_list)


    # run alg on these countries, if empty, run on all countries
    country_list = sys.argv[2] if 2 in sys.argv else \
            ["ago","bdi","ben","bfa","bwa","caf","civ","cmr","cod","cog","com","cpv","dji","dza","egy","eri","esh","eth","gab","gha","gin","gmb","gnb","gnq","ken","lbr","lby","lso","mar","mdg","mli","moz","mrt","mus","mwi","myt","nam","ner","nga","reu","rwa","sdn","sen","shn","sle","som","ssd","stp","swz","syc","tcd","tgo","tun","tza","uga","zaf","zmb","zwe","ata","atf","bvt","hmd","sgs","afg","are","arm","aze","bgd","bhr","brn","btn","cck","chn","cxr","cyp","geo","hkg","idn","ind","iot","irn","irq","isr","jor","jpn","kaz","kgz","khm","kor","kwt","lao","lbn","lka","mac","mdv","mid","mmr","mng","mys","npl","omn","pak","phl","prk","pse","qat","sau","sgp","syr","tha","tjk","tkm","tls","tur","twn","uzb","vnm","yar","yem","ymd","alb","and","aut","bel","bgr","bih","blr","blx","che","chi","csk","cze","ddr","deu","dnk","esp","est","fdr","fin","fra","fro","gbr","gib","grc","hrv","hun","imn","irl","isl","ita","ksv","lie","ltu","lux","lva","mco","mda","mkd","mlt","mne","nld","nor","pol","prt","rou","rus","scg","sjm","smr","srb","sun","svk","svn","swe","ukr","vat","yug","abw","aia","ant","atg","bes","bhs","blm","blz","bmu","brb","can","cri","cub","cuw","cym","dma","dom","grd","grl","gtm","hnd","hti","jam","kna","lca","maf","mex","msr","mtq","naa","nic","pan","pci","pcz","pri","slv","spm","tca","tto","umi","usa","vct","vgb","vir","asm","aus","cok","fji","fsm","glp","gum","kir","mhl","mnp","ncl","nfk","niu","nru","nzl","pcn","plw","png","pyf","slb","tkl","ton","tuv","vut","wlf","wsm","arg","bol","bra","chl","col","ecu","flk","guf","guy","per","pry","sur","ury","ven"]


    # run alg on these products, if empty, run on all products
    # product_list = sys.argv[3] if 3 in sys.argv else [u'15720890', u'13681091', u'18920590', u'16845910']

    product_list = set([each_prod['id'] for each_record in data_list for country_record in each_record.values() for each_prod in country_record])

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

    eps = 1e-5

    country_rank_year = {}
    product_rank_year = {}

    for idx in range(1, len(data_list) + 1):
        #if idx == 10: import pdb;pdb.set_trace()

        cum_country_country_matrix, cum_country_prod_matrix = \
                    eBip.calc_cum_transition_matrix(country_prod_matrix_list[:idx])


        # 1) run bipartite alg
        country_scores, product_scores = eBip.run_bipartite(cum_country_country_matrix, cum_country_prod_matrix, max_iter=10000, tol=eps)



        # # 2) run pagerank
        # graph = eBip.from_transition_to_matrix(cum_country_country_matrix)
        # scores, _ = eBip.run_pagerank(graph)

        # country_scores = np.ones((eBip.n_countries, ))
        # for id_, idxx in eBip.country_mapping.iteritems():
        #     country_scores[idxx] = scores[id_]




        # normalize scores
        country_scores = normalize(country_scores)
        product_scores = normalize(product_scores)

        country_id_scores = {graph.node[id_]['entity_id']:country_scores[idx] for id_, idx in eBip.country_mapping.iteritems()}
        product_id_scores = {graph.node[id_]['entity_id']:product_scores[idx] for id_, idx in eBip.product_mapping.iteritems()}

        country_id_scores = sorted(country_id_scores.iteritems(), key=lambda d:d[1], reverse=True)
        product_id_scores = sorted(product_id_scores.iteritems(), key=lambda d:d[1], reverse=True)


        # write to csv
        write_to_csv(country_id_scores, "%s/country_scores_%s.csv"%(path, idx))
        write_to_csv(product_id_scores, "%s/product_scores_%s.csv"%(path, idx))

        year = idx-1+1962
        country_rank_year[year]=country_id_scores
        product_rank_year[year]=product_id_scores


        print "\n Ranking based on the records from the Year 1 to Year %s:" % idx
        print "\ntop 10 countries"
        for id_, score in country_id_scores[:10]:
            print "%s: %s" % (id_, round(score, 2))

        print "\ntop 10 products"
        for id_, score in product_id_scores[:10]:
            print "%s: %s" % (id_, round(score, 2))

    with open("country_results.dat", 'w') as f:
        f.write(str(country_rank_year))
        f.close()
    with open("product_results.dat", 'w') as f:
        f.write(str(product_rank_year))
        f.close()


