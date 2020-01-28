import sys, os, pprint
from src import local_db, catalog_db, KG_db, spreadsheet_db, model_template
from processing.entries import find_meaningfull_alias, version_naming, reformat_for_spreadsheet

if __name__=='__main__':

    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument('-db', "--DB", default='Local') # database
    parser.add_argument('-sid', "--SheetID", type=int, default=-1,
                        help="identifier of a model instance on the spreadsheet")
    parser.add_argument('-id', "--ID", type=int, default=-1,
                        help="identifier of a model instance")
    parser.add_argument('-a', "--alias", type=str,
                        help="alias identifier of a model instance (as stated on the spreadsheet)")
    args = parser.parse_args()

    if args.DB=='Local':
        models = local_db.load_models()
    elif args.DB=='Catalog':
        models = catalog_db.load_models()

    if args.ID>=0:
        print('model %i over %i ' % (args.ID, len(models)))
        pprint.pprint(models[args.ID])
    elif args.SheetID>1:
        pprint.pprint(models[args.SheetID-2])
        # print(reformat_for_spreadsheet('images', models[args.SheetID-2]['images']))
    else:
        local_db.show_list()
    # else:
    #     for model in models:
    #         pprint.pprint(model)
    #         # if model['public']=='TRUE':
    #         #     pprint.pprint(model)
    
