from argparse import ArgumentParser, ArgumentTypeError
import json

from google_refine.refine import refine


def get_operations(project_id,rep_name):
    # get the json
    res = refine.RefineProject(refine.RefineServer(), project_id).get_operations()
    with open(f'load_recipe/{rep_name}.json', 'w') as fout:
        json.dump(res , fout,indent=4)


def Extract(project_id, rep_name, col_name):

    '''
    project id
    OpenRefine recipe name
    column name
    :return: partial JSON recipe
    '''
    get_operations(project_id,rep_name)
    rec = []
    with open(f'load_recipe/{rep_name}.json', 'r')as fin:
        data = json.load(fin)
        for d in data:
            try:
                if d['columnName'] in col_name:
                    with open(f'apply_recipe/{rep_name}.json','w')as fout:
                        rec.append(d)
                        json.dump(rec, fout, indent=4)
            except:
                pass


def project_id_file(s, sep='@'):
    if sep not in s:
        raise ArgumentTypeError(f'Separator {sep!r} not found in {s!r}.')
    project_id, project_file= s.split(sep, maxsplit=1)
    try:
        project_id=int(project_id)
    except ValueError:
        raise ArgumentTypeError(f'Project ID should be an integer. {project_id!r} is not an integer,')
    return project_id,project_file


# def col_name_split(s,sep=','):
#     col_name_list=s.split(sep)
#     return col_name_list


def Extract_parser():
    parser = ArgumentParser(description='Extract Toolkit')
    parser.add_argument(
        '-p','--projects',
        metavar='PROJ_ID@PROJ_FILE',
        nargs='+',
        type=project_id_file,
    )
    parser.add_argument(
        '-c','--colname',
        nargs='+',
    )
    parser.print_help()
    args=parser.parse_args()
    proj_file=args.projects
    # [(1577494072412, 'movie'), (1832143054149, 'company')]
    for pair in proj_file:
        proj_id=pair[0]
        rep_name=pair[1]

        colname=args.colname
        Extract(project_id=proj_id,
                rep_name=rep_name,
                col_name=colname
                )
    # movie
    # id: 1577494072412
    # company
    # id: 1832143054149
    # release
    # id: 1661067566361
    print(parser.parse_args(['-p','1577494072412@movie','1832143054149@company','-c','Mname','Director','Cname','release_date']))


def main():
    Extract_parser()
    # input project id (2 or more) waiting to merge
    # input the recipe name you want to give
    # input the column name you think they're matching


if __name__=='__main__':
    main()