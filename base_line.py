# data = "dongfang/inputdata"
# sentences = read.read_from_csv(data+".csv")
# entity_list = get_entity(sentences)

def baseline_subject_term(entity_lists):
    n_all = float(0)
    n_precise = float(0)
    for entity_list in entity_lists:
        entity_index = 0
        subject_entity = entity_list[entity_index]
        for entity in entity_list:
            if entity[5] == 'B_nBio':
                n_all +=float(1)
                if int(entity[6]) >=  subject_entity[2] and int(entity[6]) <= subject_entity[3]:

                    n_precise+=float(1)
    print "precision:", n_precise/n_all

#baseline_subject_term(entity_list)

def baseline_closest_term(entity_lists):
    n_all = float(0)
    n_precise = float(0)
    for entity_list in entity_lists:
        entity_index = 0
        for entity in entity_list:
            if entity[5] == 'B_nBio':
                n_all +=float(1)
                if entity[1] == 0:
                    subject_entity = entity_list[entity_index+1]

                elif entity[1] == len(entity_list)-1:
                    subject_entity = entity_list[entity_index - 1]

                else:
                    subject_entity1 = entity_list[entity_index -1]
                    subject_entity2 = entity_list[entity_index +1]
                    subject_entity = subject_entity1 if entity[2]-subject_entity1[3] > subject_entity1[2] - entity[3] else subject_entity2
                if int(entity[6]) >=  subject_entity[2] and int(entity[6]) <= subject_entity[3]:
                    n_precise+=float(1)
            entity_index +=1
    print "precision:", n_precise/n_all
#baseline_closest_term(entity_list)