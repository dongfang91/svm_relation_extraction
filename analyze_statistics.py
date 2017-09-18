import read_files as read
import collections


#vocab = collections.defaultdict(float)

def get_all_resources(data):
    sentences = read.read_from_csv(data+"/inputdata.csv")
    nss_terms = read.textfile2list("data/nss_terms.txt")
    nss_terms_plural = read.textfile2list("data/nss_terms_plural.txt")
    print sentences
    print nss_terms
    print nss_terms_plural
    return sentences, nss_terms,nss_terms_plural

def get_terms(sentences):
    terms = list()
    for sentence in sentences:
            for term_info in sentence:
                terms.append(term_info[1])
    return terms

def get_vocab(terms):
    vocab = collections.defaultdict(float)
    for term in terms:
        vocab[term] +=1
    return vocab

def count_nss_terms(data):
    sentences, nss_terms, nss_terms_plural = get_all_resources(data)
    terms = get_terms(sentences)
    vocab = get_vocab(terms)
    total = 0
    for nss_term_index in range(len(nss_terms)):
        counts = vocab[nss_terms[nss_term_index]]+vocab[nss_terms_plural[nss_term_index]]
        total +=counts
        print nss_terms[nss_term_index],counts

    print total

#count_nss_terms("test")
def count_ontology(file_name):
    part_of_knowledge = read.read_from_csv_ontology(file_name)
    keys = part_of_knowledge.keys()
    count = 0
    for key in keys:
        values = part_of_knowledge[key]
        print values
        count += len(values)
        print key, len(values)
    print len(keys), count

#count_ontology("test/part-of.csv")

# def get_f1(precision,recall):
#     f1 = 2*precision*recall/(precision+recall)
#     print f1
#
# get_f1( 0.9149560117302052,0.9069767441860465)









