import read_files as read
import collections




def normalize(terms):
    tokens = terms.split(' ')
    a = ''
    for token in tokens:
        a = a +' ' + plural_singular(token)
    a = a.lstrip()
    return a


def normalize_split(terms):
    import nltk
    tokens = terms.split(' ')
    tokens_original_pos = nltk.pos_tag(tokens)
    tokens_pos = []
    for token_pos in tokens_original_pos:
        if token_pos[0] == 'hilar':
            token_pos = ('hilar','NN')
        elif token_pos[0] =='pore':
            token_pos = ('pore','NN')
        elif token_pos[0] =='phyllary':
            token_pos = ('phyllary','NN')

        tokens_pos.append(token_pos)

    i = 0
    before = ''
    after = ''
    total = ''
    before_i = 0
    for token_pos in tokens_pos:
        if token_pos[1] =='NN':
            if i == len(tokens_pos) -1:
                total = terms
            else:
                before_i = i
                for k in range(i+1):
                    before = before + ' ' + tokens[k]
                for j in range(i+1,len(tokens_pos)):
                    after = after + ' ' + tokens[j]
        i = i+1
    total  = total.lstrip()
    before = before.lstrip()
    after = after.lstrip()
    return total,before,after,before_i

def get_name (index,sentence):
    name = sentence[index][1]
    end = index
    index = index +1
    last_term = ""
    while index < len(sentence) and "Bio" in sentence[index][2]:
        #print sentence[index]
        name =name + " " +sentence[index][1]
        last_term = sentence[index][1]
        end = index
        index = index +1
    return name,end,last_term

def plural_singular(token):
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    if token.endswith('ies'):
        token = token.replace('ies', 'y')
    elif token == 'cypselae':
        token = 'cypsela'
    elif token == 'rectrices':
        token = 'rectrix'
    elif token.endswith('dia'):
        token =token.replace('dia','dium')
    elif '-' in token:
        words = token.split('-')
        token = words[0] +'-'+wnl.lemmatize(words[1])
    else:
        token = wnl.lemmatize(token)
    return token.encode('utf-8')


def get_entity(sentences):
    nss_terms = read.textfile2list("data/nss_terms.txt")
    nss_terms_plural = read.textfile2list("data/nss_terms_plural.txt")
    non_specfic_terms = nss_terms + nss_terms_plural
    entity_list = []
    sid = 0
    for sentence in sentences:
        index = 0
        entity = []
        eid = 0
        if sid ==57:
            print 123
        while index < len(sentence):
            if "Bio" in sentence[index][2]:
                #print sentence[index]
                name,end,last_term = get_name(index,sentence)
                start = index
                tag = sentence[index][2]
                referent = sentence[index][3]
                if "_Bio" in sentence[index][2] and last_term != "" and plural_singular(last_term) in non_specfic_terms:
                    total, before, after, before_i = normalize_split(normalize(name))
                    entity.append ((sid,eid,start,start + before_i,before,tag,referent))
                    eid = eid + 1
                entity.append((sid,eid,start,end,name,tag,referent))      #### sentence_id, entity_id, position_start, position_end, entity_term, referent
                index = end
                eid +=1
            index = index + 1
        sid = sid+1
        entity_list.append(entity)
        #print entity
    return entity_list

def get_nbio_entity(entity_list):
    nbio_entity_list = []
    for entitys in entity_list:
        nbio_entitys = []
        for entity in entitys:
            if "B_nBio" in entity[5]:
                nbio_entitys.append(entity)
        nbio_entity_list.append(nbio_entitys)
    return nbio_entity_list


def get_entity_pair (nbio_entity_list,entity_list):
    entity_pair_list = []
    for nbio_entitys in nbio_entity_list:
        entity_pairs = []
        for nbio_entity in nbio_entitys:
            entitys = entity_list[nbio_entity[0]]
            for entity in entitys:
                if nbio_entity[1] != entity[1] and nbio_entity[3] != entity[3]:
                    if len(nbio_entity[6])>0 and int(nbio_entity[6]) >= entity[2] and int(nbio_entity[6]) <= entity[3]:
                        entity_pairs.append((nbio_entity,entity,"+1"))
                    else:
                        entity_pairs.append((nbio_entity, entity, "-1"))

        if entity_pairs:
            #print entity_pairs
            entity_pair_list.append(entity_pairs)

    return entity_pair_list

def get_data(data):
    sentences = read.read_from_csv(data+".csv")
    entity_list = get_entity(sentences)
    nbio_entity_list = get_nbio_entity(entity_list)
    entity_pair_list = get_entity_pair (nbio_entity_list,entity_list)
    #print len(entity_pair_list)
    return sentences, entity_list,nbio_entity_list,entity_pair_list

def get_positive_entity_pair (nbio_entity_list,entity_list):
    entity_pair_list = []
    for nbio_entitys in nbio_entity_list:
        entity_pairs = []
        for nbio_entity in nbio_entitys:
            entitys = entity_list[nbio_entity[0]]
            for entity in entitys:
                if nbio_entity[1] != entity[1] and nbio_entity[3] != entity[3]:
                    if len(nbio_entity[6])>0 and int(nbio_entity[6]) >= entity[2] and int(nbio_entity[6]) <= entity[3]:
                        entity_pairs.append((nbio_entity,entity,"+1"))
        if entity_pairs:
            entity_pair_list.append(entity_pairs)
    return entity_pair_list

def get_sentence(sentences):
    """
    sentences to lists
    :param sentences:
    :return:
    """
    texts = []

    vocab = collections.defaultdict(float)
    for statement in sentences:
        text = [token[1] for token in statement]
        texts.append(text)
    vocab = read.get_vocab(read.lists2list(texts))

    return texts, vocab

def judge_closest(entity_pair,entity_list):
    entity_id = entity_pair[0][1]
    anchor_id = entity_pair[1][1]

    if entity_id == 0:
        subject_entity = entity_list[entity_id+1]
    elif entity_id == len(entity_list) - 1:
        subject_entity = entity_list[entity_id - 1]
    else:
        subject_entity1 = entity_list[entity_id - 1]
        subject_entity2 = entity_list[entity_id + 1]
        subject_entity = subject_entity1 if entity_pair[0][2] - subject_entity1[3] > subject_entity1[2] - entity_pair[0][3] else subject_entity2

    a = float(1) if subject_entity[1] == anchor_id else float(0)
    return a

def judge_ontology(entity_pair, part_of_knowledge):
    non_entity = normalize(entity_pair[0][4])
    entity = normalize(entity_pair[1][4])
    if part_of_knowledge.has_key(entity) and non_entity in part_of_knowledge.get(entity):
        is_in_ontology = float(1)
    else:
        is_in_ontology = float(0)
    return is_in_ontology

def get_bag_of_word(entity_pair,texts,vocab,connectors,threshold):
    word_dict = {}
    sentence = texts[entity_pair[0][0]]
    n_len = len(sentence)
    non_entity = entity_pair[0]
    entity = entity_pair[1]
    bagwords = list()
    if non_entity[2]<=threshold:
        bagwords+=sentence[0:non_entity[2]]
    else:
        bagwords += sentence[non_entity[2]-threshold:non_entity[2]]

    if entity[2]<=threshold:
        bagwords+=sentence[0:entity[2]]
    else:
        bagwords += sentence[entity[2]-threshold:entity[2]]

    if n_len - threshold-1 <= non_entity[3] < n_len -1:
        bagwords += sentence[non_entity[3]+1:n_len]
    elif non_entity[3] == n_len -1:
        None
    else:
        bagwords += sentence[non_entity[3]+1:non_entity[3]+1+threshold]

    if n_len - threshold-1 <= entity[3] < n_len -1:
        bagwords += sentence[entity[3]+1:n_len]
    elif entity[3] == n_len -1:
        None
    else:
        bagwords += sentence[entity[3]+1:entity[3]+1+threshold]

    if non_entity[3] < entity[2]-1:
        bagwords += [item  for item in sentence[non_entity[3]+1:entity[2]] if item in connectors]
    elif entity[3] < non_entity[2]-1:
        bagwords += [item for item in sentence[entity[3] + 1:non_entity[2]] if item in connectors]

    bagwords = list(set(bagwords))
    vocab = list(set(vocab+connectors))
    for item in vocab:
        word_dict[item] = float(1) if item in bagwords else float(0)

    return word_dict



def build_features(features,entity_list,nbio_entity_list,entity_pair_list,part_of_knowledge,texts,vocab,connectors,threshold):

    feature_strs = ""


    for entity_pairs in entity_pair_list:
        for entity_pair in entity_pairs:
            feature_strs += "%s" % (entity_pair[2])
            print entity_pair
            ##### Distance and position features#######
            is_subject_entity = float(1) if entity_pair[1][1] ==0 else float(0)
            is_closest_entity = judge_closest(entity_pair,entity_list[entity_pair[0][0]])
            absolute_distance = float(entity_pair[1][2] - entity_pair[0][3]) if entity_pair[1][2] > entity_pair[0][3] else float(entity_pair[1][3] - entity_pair[0][2])
            absolute_entity_num = float(entity_pair[1][1] - entity_pair[0][1])
            relative_distance = absolute_distance/float(len(texts[entity_pair[0][0]]))
            relative_entity_num = absolute_entity_num / float(len(entity_list[entity_pair[0][0]]))
            is_in_ontology = judge_ontology(entity_pair, part_of_knowledge)
            is_nbio = float(1) if entity_pair[1] in nbio_entity_list[entity_pair[0][0]]  else float(0)

            word_dict = get_bag_of_word(entity_pair,texts,vocab,connectors,threshold)

            # feature_strs += " subject_entity:%f" % (is_subject_entity)
            # feature_strs += " is_closest_entity:%f" % (is_closest_entity)
            # feature_strs += " absolute_distance:%f" % (absolute_distance)
            # feature_strs += " absolute_entity_num:%f" % (absolute_entity_num)
            # feature_strs += " relative_distance:%f" % (relative_distance)
            # feature_strs += " relative_entity_num:%f" % (relative_entity_num)
            # feature_strs += " is_in_ontology:%f" % (is_in_ontology)
            # feature_strs += " is_nbio:%f" % (is_nbio)
            # for key,value in word_dict.items():
            #     feature_strs += " "+str(key)+":%f"% (value)
            # feature_strs += "\n"

            feature_strs += " 0:%f" % (is_subject_entity)
            feature_strs += " 1:%f" % (is_closest_entity)
            feature_strs += " 2:%f" % (absolute_distance)
            feature_strs += " 3:%f" % (absolute_entity_num)
            feature_strs += " 4:%f" % (relative_distance)
            feature_strs += " 5:%f" % (relative_entity_num)
            feature_strs += " 6:%f" % (is_in_ontology)
            feature_strs += " 7:%f" % (is_nbio)

            fea_index = 6
            for key,value in word_dict.items():
                feature_strs += " "+str(fea_index)+":%f"% (value)
                fea_index+=1

            feature_strs += "\n"

    output_file1 = file('data/'+features+'.txt', 'w+')
    output_file1.write(feature_strs)
    output_file1.close()
    print "Done."



data = "test/inputdata"
part_of = "test/part-of.csv"
feature1 = "all"
features = "test/all"

# feature1 = "all_withoutonto"
# features = "dongfang/all_withoutonto"


# data = "dev/inputdata1"
# part_of = "thomas/part-of1.csv"

# feature1 = "all_withoutonto"
# features = "dev/all_withoutonto"

# feature1 = "all"
# features = "dev/all"

#data = "test/inputdata"
sentences, entity_list,nbio_entity_list,entity_pair_list = get_data(data)
connectors = ['at','in','on','of','has','have','with','without','contains','contain']
part_of_knowledge = read.read_from_csv_ontology(part_of)
texts, vocab = get_sentence(sentences)
#print len(texts)
#read.save_in_json("dev/vocab",vocab)
vocab = read.read_from_json("dev/vocab")
new_vocab = [item for item,freq in vocab.items() if freq >=9]

threshold = 4
#build_features(features,entity_list,nbio_entity_list,entity_pair_list,part_of_knowledge,texts,new_vocab,connectors,threshold)


#
from svmutil import *
y1,x1 = svm_read_problem('data/'+features+'.txt')


# model = svm_train(y1, x1,'-t 2 -b 1 -w1 7 -w-1 1 -h 0')  # -w1 8 -w-1 1')  -v 5
# svm_save_model('data/thomas/relation_extraction_'+feature1+'.model', model)

model = svm_load_model('data/dev/relation_extraction_'+feature1+'.model')
import evaluate as test
test.evaluate(feature1,nbio_entity_list,entity_pair_list,model,y1,x1)


predicted = read.read_from_json('test/evaluation_all')

test.error_analysis(predicted,texts)
