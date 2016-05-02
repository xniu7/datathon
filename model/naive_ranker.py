import numpy as np
from collections import defaultdict, OrderedDict
import sys
import os
from evol_bipartite import load_all_data, load_im_ex_data

path = "results/naive"


class NaiveRanker:
    def __init__(self, country_list, product_list):
        self.country_list,  self.product_list = country_list, product_list


    def rank(self, import_export_data):
        """
        rank countries based on trade balance
        rank products based on import values
        """


        country_profit = defaultdict(float)
        product_im_val = defaultdict(float)

        for country, records in import_export_data.iteritems():
            if not country in self.country_list:
                continue

            for each_record in records:
                if not each_record['id'] in self.product_list:
                    continue


                country_profit[country] += each_record['export'] - each_record['import']

                product_im_val[each_record['id']] += each_record['import']


        # sort
        country_profit = OrderedDict(sorted(country_profit.iteritems(), key=lambda d:d[1], reverse=True))
        product_im_val = OrderedDict(sorted(product_im_val.iteritems(), key=lambda d:d[1], reverse=True))

        return country_profit, product_im_val




    def cum_rank(self, country_profit_list, product_im_val_list):
        # compute avg scores
        cum_country_profit = defaultdict(float)
        cum_product_im_val = defaultdict(float)

        # country
        for country_profit in country_profit_list:
            for country, profit in country_profit.iteritems():
                cum_country_profit[country] += profit

        # for product
        for product_im_val in product_im_val_list:
            for product, im_val in product_im_val.iteritems():
                cum_product_im_val[product] += im_val

        # avg
        for country, profits in cum_country_profit.iteritems():
            cum_country_profit[country] = profits / float(len(country_profit_list))

        for product, im_val in cum_product_im_val.iteritems():
            cum_product_im_val[product] = im_val / float(len(product_im_val_list))


         # sort
        cum_country_profit = OrderedDict(sorted(cum_country_profit.iteritems(), key=lambda d:d[1], reverse=True))
        cum_product_im_val = OrderedDict(sorted(cum_product_im_val.iteritems(), key=lambda d:d[1], reverse=True))


        return cum_country_profit, cum_product_im_val



    def calc_score_list(self, data_list):
        country_profit_list = []
        product_im_val_list = []

        for import_export_data in data_list:
            country_profit, product_im_val = self.rank(import_export_data)

            country_profit_list.append(country_profit)
            product_im_val_list.append(product_im_val)

        return country_profit_list, product_im_val_list



    def rank_each_year(self, data_list):

        idx = 1
        for import_export_data in data_list:
            country_profit, product_im_val = self.rank(import_export_data)

            # normalize
            country_profit = dict_normalize(country_profit)
            product_im_val = dict_normalize(product_im_val)

            # write to disk
            write_to_csv(country_profit, name="%s/country_scores_%s.csv"%("%s/single"%path, idx))
            write_to_csv(product_im_val, name="%s/product_scores_%s.csv"%("%s/single"%path, idx))

            idx += 1

            print "\ntop 10 countries"
            for id_, score in country_profit[:10]:
                print "%s: %s" % (id_, round(score, 2))

            print "\ntop 10 products"
            for id_, score in product_im_val[:10]:
                print "%s: %s" % (id_, round(score, 2))



def dict_normalize(x):

    vals = np.array(x.values())
    max_, min_ = np.max(vals), np.min(vals)
    vals = (vals - min_) * 100 / (max_ - min_) if not max_ == min_ else 100 * x / max_

    vals = (vals * 100.0 / np.sum(vals)).tolist()
    xx = zip(x.keys(), vals)

    return xx


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

    if not os.path.exists("%s/cum"%path):
        os.makedirs("%s/cum"%path)

    if not os.path.exists("%s/single"%path):
        os.makedirs("%s/single"%path)


    if len(sys.argv) > 1:
        file_list = sys.argv[1:]
    else:
        data_root = "../data/cum"

        # years = range(2011, 2014)
        years = range(1962, 2015)
        file_list = ["%s/%s"%(data_root, y) for y in years]


    print "# of data files: %s" % len(file_list)



    # load all data
    data_list = load_all_data(file_list)


    # run alg on these countries, if empty, run on all countries
    country_list = sys.argv[2] if 2 in sys.argv else \
            ["ago","bdi","ben","bfa","bwa","caf","civ","cmr","cod","cog","com","cpv","dji","dza","egy","eri","esh","eth","gab","gha","gin","gmb","gnb","gnq","ken","lbr","lby","lso","mar","mdg","mli","moz","mrt","mus","mwi","myt","nam","ner","nga","reu","rwa","sdn","sen","shn","sle","som","ssd","stp","swz","syc","tcd","tgo","tun","tza","uga","zaf","zmb","zwe","ata","atf","bvt","hmd","sgs","afg","are","arm","aze","bgd","bhr","brn","btn","cck","chn","cxr","cyp","geo","hkg","idn","ind","iot","irn","irq","isr","jor","jpn","kaz","kgz","khm","kor","kwt","lao","lbn","lka","mac","mdv","mid","mmr","mng","mys","npl","omn","pak","phl","prk","pse","qat","sau","sgp","syr","tha","tjk","tkm","tls","tur","twn","uzb","vnm","yar","yem","ymd","alb","and","aut","bel","bgr","bih","blr","blx","che","chi","csk","cze","ddr","deu","dnk","esp","est","fdr","fin","fra","fro","gbr","gib","grc","hrv","hun","imn","irl","isl","ita","ksv","lie","ltu","lux","lva","mco","mda","mkd","mlt","mne","nld","nor","pol","prt","rou","rus","scg","sjm","smr","srb","sun","svk","svn","swe","ukr","vat","yug","abw","aia","ant","atg","bes","bhs","blm","blz","bmu","brb","can","cri","cub","cuw","cym","dma","dom","grd","grl","gtm","hnd","hti","jam","kna","lca","maf","mex","msr","mtq","naa","nic","pan","pci","pcz","pri","slv","spm","tca","tto","umi","usa","vct","vgb","vir","asm","aus","cok","fji","fsm","glp","gum","kir","mhl","mnp","ncl","nfk","niu","nru","nzl","pcn","plw","png","pyf","slb","tkl","ton","tuv","vut","wlf","wsm","arg","bol","bra","chl","col","ecu","flk","guf","guy","per","pry","sur","ury","ven"]


    # run alg on these products, if empty, run on all products
    product_list = set([each_prod['id'] for each_record in data_list for country_record in each_record.values() for each_prod in country_record])


    nr = NaiveRanker(country_list, product_list)
    # import pdb;pdb.set_trace()

    # rank for each single year
    nr.rank_each_year(data_list)

    # import pdb;pdb.set_trace()

    # cumulative rank
    country_profit_list, product_im_val_list = nr.calc_score_list(data_list)

    # import pdb;pdb.set_trace()
    for idx in range(1, len(data_list) + 1):
        cum_country_profit, cum_product_im_val = nr.cum_rank(country_profit_list[:idx], product_im_val_list[:idx])


        # normalize
        cum_country_profit = dict_normalize(cum_country_profit)
        cum_product_im_val = dict_normalize(cum_product_im_val)
        # import pdb;pdb.set_trace()
        # write to disk
        write_to_csv(cum_country_profit, name="%s/country_scores_%s.csv"%("%s/cum"%path, idx))
        write_to_csv(cum_product_im_val, name="%s/product_scores_%s.csv"%("%s/cum"%path, idx))


        print "\n Ranking based on the records from the Year 1 to Year %s:" % idx

        print "\ntop 10 countries"
        for id_, score in cum_country_profit[:10]:
            print "%s: %s" % (id_, round(score, 2))

        print "\ntop 10 products"
        for id_, score in cum_product_im_val[:10]:
            print "%s: %s" % (id_, round(score, 2))





