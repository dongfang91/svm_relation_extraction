import json
import h5py
import numpy as np
import csv
import collections


def save_in_json(filename, array):
    with open('data/'+filename+'.txt', 'w') as outfile:
        json.dump(array, outfile)
    outfile.close()

def read_from_json(filename):
    with open('data/'+filename+'.txt', 'r') as outfile:
        data = json.load(outfile)
    outfile.close()
    return data


def read_from_csv(filename):
    sentences = []
    sentence = []
    with open('data/'+filename, 'rb') as mycsvfile:
        thedata = csv.reader(mycsvfile)
        for row in thedata:
            if "sentence>" not in row[0] and row:
                k = (int(row[0]), unicode(row[1], 'ISO-8859-1').encode('utf-8'), row[2], row[3])
                # k.append((row[0].))
                sentence.append(k)

            elif sentence != []:
                sentences.append(sentence)
                sentence = []
    return sentences

def read_from_csv_ontology(filename):
    with open('data/'+filename, 'rb') as mycsvfile:
        part_of = csv.reader(mycsvfile)
        part_of_knowledge = {}
        for row in part_of :
            value = []
            value.append(row[1])
            if part_of_knowledge.has_key(row[0]) == False:
                part_of_knowledge[row[0]] =value
            else:
                values = part_of_knowledge.get(row[0])
                values = values +value
                part_of_knowledge[row[0]] = values
    return part_of_knowledge

def read_json(filename):
    with open(filename+'.txt', 'r') as outfile:
        data = json.load(outfile)
    outfile.close()
    return data

def save_json(filename, array):
    with open(filename+'.txt', 'w') as outfile:
        json.dump(array, outfile)
    outfile.close()

def read_from_dir(path):
    data =open(path).read()
    return data

def textfile2list(path):
    data = read_from_dir(path)
    list_new =list()
    for line in data.splitlines():
        list_new.append(line)
    return list_new

def load_input(filename):
    with h5py.File('data/'+ filename + '.hdf5', 'r') as hf:
        print("List of arrays in this file: \n", hf.keys())
        x = hf.get('input')
        y = hf.get('output')
        x_data = np.array(x)
        #n_patterns = x_data.shape[0]
        y_data = np.array(y)
        # print x_data[0][1000:1100]
        # print y_data[0][1000:1100]
        #y_data = y_data.reshape(y_data.shape+(1,))
        print x_data.shape
        print y_data.shape


    del x
    del y
    return x_data,y_data

def load_pos(filename):
    with h5py.File('data/'+ filename + '.hdf5', 'r') as hf:
        print("List of arrays in this file: \n", hf.keys())
        x = hf.get('input')

        x_data = np.array(x)
        #n_patterns = x_data.shape[0]

        # print x_data[0][1000:1100]
        # print y_data[0][1000:1100]
        #y_data = y_data.reshape(y_data.shape+(1,))
        print x_data.shape
    del x
    return x_data


def counterList2Dict (counter_list):
    dict_new = dict()
    for item in counter_list:
        dict_new[item[0]]=item[1]
    return dict_new

def get_vocab(terms):
    vocab = collections.defaultdict(float)
    for term in terms:
        vocab[term] +=1
    return vocab

def lists2list(list_as):
    k = list()
    for list_a in list_as:
        for item in list_a:
            k.append(item)
    return k