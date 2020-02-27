import sys, os, pprint, numpy, time
from mc_src import local_db, catalog_db, KG_db, spreadsheet_db, model_template
from processing.entries import find_meaningfull_alias, version_naming, reformat_for_spreadsheet


def print_key_val(key, val):
    """
    """
    if type(val) is str:
        print('- %s:' % key)
        print('                 %s' % val)
    elif type(val) is tuple:
        print('- %s:' % key)
        print('                * name: %s' % (val[0]))
        print('                * KG ID: %s' % (val[1]))
    elif type(val) is dict:
        print('- %s:' % key)
        for k, v in val.items():
            print('                * %s: %s' % (k, v))
    else:
        print(key, val)
            

def nice_model_print(model):

    keys = list(model.keys())
    keys.sort()

    for key in keys:
        if type(model[key]) is list:
            for i, vval in enumerate(model[key]):
                print_key_val('%s %s' % (key, i+1), vval)
        else:
                print_key_val(key, model[key])
        
if __name__=='__main__':

    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument('-db', "--DB", default='Local') # database
    parser.add_argument('-sid', "--SheetID", type=int, default=1,
                        help="identifier of a model instance on the spreadsheet")
    parser.add_argument('-id', "--ID", type=int, default=-1,
                        help="identifier of a model instance")
    parser.add_argument('-a', "--alias", type=str,
                        help="alias identifier of a model instance (as stated on the spreadsheet) [TO BE IMPLEMENTED]")
    parser.add_argument('-k', "--key", type=str,
                        help="key to be shown", default='')
    args = parser.parse_args()


    if args.SheetID>1:
        args.ID = args.SheetID-1

    def print_list_or_single_model(models, args):
        if args.ID>0 and args.key!='':
            print('* %i) %s' % (args.ID, models[args.ID-1]['name']))
            print('        %s: %s' % (args.key, models[args.ID-1][args.key]))
        elif args.ID>0:
            print('model %i over %i ' % (args.ID, len(models)))
            nice_model_print(models[args.ID-1])
        else:
            for i, model in zip(range(len(models))[::-1], models[::-1]):
                print('* %i) %s' % (i+1, model['name']))
                if args.key!='':
                    print('     %s: %s' % (args.key, model[args.key]))
        
    if args.DB=='Local':
        models = local_db.load_models()
    elif args.DB=='Catalog':
        models = catalog_db.load_models()
    elif args.DB=='KGnexus':
        models = KG_db.fetch_models(api='nexus')
    elif args.DB=='KGreleased':
        models = KG_db.fetch_models(scope='released')
    elif args.DB=='KGinferred':
        models = KG_db.fetch_models(scope='inferred')
    print_list_or_single_model(models, args)

    
