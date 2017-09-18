import csv
from nltk.stem import WordNetLemmatizer
from svmutil import *

def get_previous_pair(pairs, i):
    previous_pairs  = []

    sid = pairs[i][0]
    eid = pairs[i][1]

    while pairs[i-1][0] ==sid and pairs[i-1][1] == eid:
        previous_pairs.append(pairs[i-1][7:])
        i = i-1
    return previous_pairs

def plural_singular(token):
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


def normalize(terms):
    tokens = terms.split(' ')
    a = ''
    for token in tokens:
        a = a +' ' + plural_singular(token)
    a = a.lstrip()
    return a

def get_precision_and_recall(version):
    pairs = []
    with open('data/thomas/predic_pairs_'+ version +'.csv', 'rb') as mycsvfile:
        pair_result = csv.reader(mycsvfile)
        for row in pair_result:
            pairs.append(row)
    pairs = pairs[1:]

    with open('data/thomas/precision_' + version + '.csv', 'wb') as out:
        csv_out1 = csv.writer(out)
        num = len(pairs)
        for i in range(num - 1):
            if pairs[i][0] != pairs[i + 1][0] or pairs[i][1] != pairs[i + 1][1]:
                row = pairs[i]
                if i > 0:
                    previous_pairs = get_previous_pair(pairs, i)
                    for previous_pair in previous_pairs:
                        row = row + previous_pair
                csv_out1.writerow(row)

    with open('data/thomas/precision_' + version +'.csv', 'rb') as mycsvfile:
        pair_result = csv.reader(mycsvfile)
        j = 0
        prediction_true = 0
        prediction_wrong = 0
        prediction_true_additional_prediction = 0
        for row in pair_result:
            j = j + 1.0
            num_dec = (len(row) - 7) / 9

            if num_dec == 1:
                if (row[15] == '1.0'):
                    prediction_true += 1.0
                else:
                    prediction_wrong += 1.0

            else :
                k = False
                t = True
                for i in range(num_dec):
                    k = (row[6 + i * 9 + 8] == '+1' and row[6 + i * 9 + 9] == '1.0') or k
                    t = (normalize(row[6 + 5]) == normalize(row[6 + i*9 + 5] )) and t
                if k == True:

                    if( t == True):
                        prediction_true +=1.0

                    else:
                        prediction_true_additional_prediction += 1.0
                else:
                    prediction_wrong += 1.0
        return j,prediction_true, prediction_wrong, prediction_true_additional_prediction

def get_true(bio_list):
    for bio in bio_list:
        if int(bio[7]) ==1:
            return bio

def evaluate(feature1,nbio_entity_list,entity_pair_list,model,y1,x1):

    import numpy as np
    import read_files as read
    p_lab, p_acc, p_vals = svm_predict(y1, x1, model, options="-b 1")
    p_vals_1 = np.asarray(p_vals)[:, 0]
    nbio_entity_list = read.lists2list(nbio_entity_list)
    entity_pair_list = read.lists2list(entity_pair_list)

    pair_wise = dict()
    key_list = list()

    for nbio_entity in nbio_entity_list:
        sid = nbio_entity[0]
        eid = nbio_entity[1]
        key_list.append(str(sid) + "_" + str(eid))


    index = 0
    for entity_pair in entity_pair_list:
        sid = entity_pair[0][0]
        eid = entity_pair[0][1]
        key = str(sid)+"_"+str(eid)

        if not pair_wise.has_key(key):
            label = [int(entity_pair[2])]
            pair_wise[key] =[[list(entity_pair[1])+label],[p_vals_1[index]]]
        else:
            value =pair_wise[key]
            bio_list,pro_list = value
            label = [int(entity_pair[2])]
            bio_list.append(list(entity_pair[1])+label)
            pro_list.append(p_vals_1[index])
            pair_wise[key] = [bio_list,pro_list]
        index +=1

    correct = 0
    index = 0
    answers = list()
    for key in key_list:
        bio_list, pro_list = pair_wise[key]
        i = np.argmax(pro_list)
        if bio_list[i][7] == 1:
            correct+=1
            answers.append([nbio_entity_list[index],bio_list[i]])
        else:
            answers.append([nbio_entity_list[index], bio_list[i],get_true(bio_list)])
        index+=1

    read.save_in_json('dongfang/evaluation_'+feature1,answers)

    precision = float(correct)/float(index)
    print precision,correct,all


def save_file_and_get_precision(version, entity_pair_predics):
    # with open('total_predic_pairs_'+ version +'.csv','wb') as out:
    #     csv_out=csv.writer(out)
    #     csv_out.writerow(['name','num'])
    #     for row in entity_pair_predics:
    #         csv_out.writerow(row)

    with open('data/thomas/predic_pairs_'+ version +'.csv','wb') as out:
        csv_out1 = csv.writer(out)
        csv_out1.writerow(['n_sid','n_eid','n_start','n_end','n_token','n_label','n_referent','sid','eid','start','end','token','label','referent','true_relation','predict_relation'])
        for row in entity_pair_predics:
            if row[2] == '+1' or row[3] ==1.0:
                a = list(row[0]+row[1])
                a.append(row[2])
                a.append(row[3])
                print row[2],row[3]
                csv_out1.writerow(a)

def error_analysis (predicted,texts):
    with open('data/dongfang/error_analysis.csv', 'wb') as out:
        csv_out1 = csv.writer(out)
        csv_out1.writerow(
            ['text','n_sid', 'n_eid', 'n_start', 'n_end', 'n_token', 'n_label', 'n_referent', 'p_sid', 'p_eid', 'p_start', 'p_end',
             'p_token', 'p_label', 'p_referent', 't_sid','t_eid', 't_start', 't_end',
             't_token', 't_label', 't_referent' ])

        for pair in predicted:
                #print positive_entity_pair
            a = list()
            a.append(texts[pair[0][0]])
            a+= list(pair[0])
            a += list(pair[1])
            if pair[1][7] ==-1:
                a +=list(pair[2])
            csv_out1.writerow(a)










