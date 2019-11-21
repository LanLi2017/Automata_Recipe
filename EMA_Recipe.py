'''
E : Extract
M : Merge
A : Apply
Recipe
'''
import csv
import json
import pandas as pd

# from .google.refine import refine
from google_refine.refine import refine


def apply_operations(project_id,file_path):
    # apply operations: apply the json file
    return refine.RefineProject(refine.RefineServer(),project_id).apply_operations(file_path)


def get_operations(project_id,rep_name):
    # get the json
    res = refine.RefineProject(refine.RefineServer(), project_id).get_operations()
    with open(f'load_recipe/{rep_name}.json', 'w') as fout:
        json.dump(res , fout,indent=4)


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
        reader1,reader2=pd.read_csv(file1,index_col=False),pd.read_csv(file2,index_col=False)
        key=[]
        for i,col1 in enumerate(reader1):
            for j,col2 in enumerate(reader2):
                if reader1.loc[:,col1].equals(reader2.loc[:,col2]):
                    # print(reader1.loc[:,col1])
                    # print(reader2.loc[:,col2])
                    key.append(col1)
        print(key)
        return key

# get multiple json files through or-py-client
# extract key information
# combine into one load_recipe
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
    :return:
    '''
    pro_id='1661067566361'
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
            key_list=schema_matching('release',recipe_name)
            recipe_path=f'load_recipe/{recipe_name}.json'
            get_operations(project_id=project_id,rep_name=recipe_name)

            # get the extraction part
            list_dicts+=Extract_Merge(key_list,recipe_path)
        else:

            break
    # create new JSON file: release.json
    apply_rep_name=input("input the applying recipe name:")
    apply_rep_path=f'apply_recipe/{apply_rep_name}.json'
    with open(apply_rep_path,'w')as f:
        json.dump(list_dicts,f,indent=4)

    # apply through or-py-client
    apply_operations(pro_id, apply_rep_path)

    # pass
    # get_operations('1760448733111','test')


if __name__=='__main__':
    main()
