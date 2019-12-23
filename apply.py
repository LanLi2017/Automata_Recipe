import json
from argparse import ArgumentParser, ArgumentTypeError

from google_refine.refine import refine


def apply_operations(project_id,file_path):
    # apply operations: apply the json file
    return refine.RefineProject(refine.RefineServer(),project_id).apply_operations(file_path)


def PK_FK(s,sep='@'):
    '''
    
    :param s: Mname@Movie Mdate@Date 
    :param sep: 
    :return: [('Mname','Movie'), ('Mdate','Date'),...]
    '''
    if sep not in s:
        raise ArgumentTypeError(f'Separator {sep!r} not found in {s!r}.')
    pk_col, fk_col=s.split(sep, maxsplit=1)
    return pk_col,fk_col


def convert_key(obj,convert_func):
    if isinstance(obj,list):
        return [
            convert_key(item,convert_func)
            for item in obj
        ]
    elif isinstance(obj,dict):
        return {
            convert_func(key): convert_key(value, convert_func)
            for key, value in obj.items()
        }
    else:
        return obj


def Apply_parser():
    parser = ArgumentParser(description='Apply Toolkit')
    parser.add_argument(
        '-p','--projects',
        nargs='+',
    )
    parser.add_argument(
        '-f','--filename',
        nargs='+',
    )
    parser.add_argument(
        '-c','--columns',
        metavar='PK_COLNAME@FK_COLNAME',
        nargs='+',
        type=PK_FK,
    )

    parser.print_help()
    args=parser.parse_args()
    proj_id=args.projects

    # deal with the primary key, foreign key
    pk_fk=args.columns
    # [('Mname', 'Movie'), ('Mdate', 'Date'), ...]

    filename=args.filename

    for f in filename:
        filepath=f'apply_recipe/{f}.json'
        # replace the primary key into foreign key
        with open(filepath, 'r+')as fin:
            data = json.load(fin)
            for d in data:
                for pair in pk_fk:
                    pk=pair[0]
                    fk=pair[1]
                    try:
                        if d['columnName']==pk:
                            d['columnName']=fk
                            fin.seek(0)
                            json.dump(data, fin, indent=4)
                            fin.truncate()

                    except:
                        pass

        #
        apply_operations(project_id=proj_id,file_path=filepath)


def main():
    Apply_parser()
    '''
    test
    release id: 1661067566361
    '''


if __name__=='__main__':
    main()
