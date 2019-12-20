'''
E : Extract
M : Merge
A : Apply
Recipe
'''
import csv
import json
from collections import Counter

import pandas as pd

# from .google.refine import refine
from google_refine.refine import refine


def apply_operations(project_id,file_path):
    # apply operations: apply the json file
    return refine.RefineProject(refine.RefineServer(),project_id).apply_operations(file_path)


def get_operations(project_id,rep_name):
    # get the json
    res = refine.RefineProject(refine.RefineServer(), project_id).get_operations()
    with open(f'load_reacipe/{rep_name}.json', 'w') as fout:
        json.dump(res , fout,indent=4)


def similarity(x):
    return x[2]


def slice_top(sequence, key_func=None):
    """

    :param sequence: input the list of lists
    :param key_func: optional one-argument ordering function
    :return:sliced sequence index
    """
    if not sequence:
        raise ValueError('empty sequence')

    if not key_func:
        key_func = similarity

    index=0
    for item in sequence:
        if key_func(item)==1.0:
           # ranked list of the matching columns
           index=sequence.index(item)
           break
    return index


# schema matching
def schema_matching(control_tb,compare_tb):
    '''
    control_tb: release.csv
    compare_tb: company/movie.csv
    :return: possible key columns
    '''
    control_tb_path=f'raw_dataset/{control_tb}.csv'
    compare_tb_path=f'raw_dataset/{compare_tb}.csv'
    with open(control_tb_path,'r')as file1,\
        open(compare_tb_path,'r')as file2:
        table_1,table_2=pd.read_csv(file1,index_col=False),pd.read_csv(file2,index_col=False)
        schema_matching_matric=[]
        for col_1 in table_1.columns:
            for col_2 in table_2.columns:
                value_1=Counter(table_1[col_1])
                value_2=Counter(table_2[col_2])
                similarity = len((value_1 | value_2) - (value_1 & value_2))
                norm_simi = similarity / (len(value_1) + len(value_2))
                schema_matching_matric.append([col_1,col_2,norm_simi])
        sort_sm=sorted(schema_matching_matric,key=lambda x: x[2])
        key=[]
        # take the top 2
        index=slice_top(sort_sm)
        res_sm=sort_sm[:index]
        for item in res_sm:
            key.append(item[0])
        # key.append(res_sm,key=lambda x:x[0])
        print(key)
        return key


# get multiple json files through or-py-client
# extract key information
# combine into one load_recipe
# disjoint pre-suppose
def Extract_Merge(fk,json_path):
    '''

    :param fk: the extraction part, key -> column name
    :param json_path: load_recipe path
    :return: list of dictionary
    '''
    rec=[]
    with open(f'{json_path}','r')as f:
         data=json.load(f)
         for d in data:
             try:
                 if d['columnName'] in fk:
                     rec.append(d)
             except:
                 pass

    return rec


def prompt_int(message, min=None, max=None):
    while True:
        input_str = input(message)

        try:
            value = int(input_str)

            if min is not None and value < min:
                raise ValueError
            if max is not None and value > max:
                raise ValueError

        except ValueError:
            pass
        else:
            return value


def prompt_option(options):
    for idx,option in enumerate(options,start=1):
        print(idx,option)

    if not options:
        return 0
    else:
        return prompt_int('Please enter your choice: ', min=1, max=len(options))


def main():
    '''
    movie id: 1577494072412
    company id: 1832143054149
    release id: 1661067566361
    :return:
    '''
    # pro_id='1661067566361'
    list_dicts=[]
    while True:
        choice=prompt_option([
            'Keep input',
            'Exit',
        ])
        if choice==1:
            # get load_recipe by py-client library
            project_id = input("Input the project id: ")
            recipe_name=input("Give the load_recipe name: ")
            '''
            integrated ....should not be constant 
            '''
            key_list=schema_matching('release',recipe_name)
            recipe_path=f'load_recipe/{recipe_name}.json'
            get_operations(project_id=project_id,rep_name=recipe_name)

            # get the extraction part
            list_dicts+=Extract_Merge(key_list,recipe_path)
        else:
            pro_id=input("Input the integrated project id:")
            apply_rep_name = input("input the applying recipe name:")
            apply_rep_path = f'apply_recipe/{apply_rep_name}.json'

            break
    # create new JSON file: release.json

    with open(apply_rep_path,'w')as f:
        json.dump(list_dicts,f,indent=4)

    # apply through or-py-client
    apply_operations(pro_id, apply_rep_path)


if __name__=='__main__':
    main()
