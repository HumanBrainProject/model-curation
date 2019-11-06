import sys, os, pprint
import numpy as np

from src import local_db, catalog_db, KG_db, spreadsheet_db, model_template
from processing.entries import refactor_model_entries

def from_catalog_to_local_db(new_entries_only=True):

    models = catalog_db.load_models()

    if new_entries_only:
        previous_models = local_db.load_models()
        print('number of models before update from Catalog: %i' % len(previous_models))
        name_previous_models = [m['name'] for m in previous_models]
    else:
        previous_models = []
        name_previous_models = []
    
    new_models = previous_models
    
    for model in models:

        # the Catalog DB can only update new entries to the DB
        if (model['name'] not in name_previous_models):

            model_to_be_added = model_template.template.copy()
            # dealing with the keys in common
            for key, val in model_template.template.items():
                if key in model:
                    if type(val) is tuple:
                        model_to_be_added[key] = (model[key], "")
                    else:
                        model_to_be_added[key] = model[key]
                if key=='creation_date':
                    model_to_be_added[key] = model[key][:19]

            if len(model['instances'])==0: # if no version, an entry with version ""
                model_to_be_added['version'] = ''
                new_models.append(model_to_be_added)
            else: # we add one model per version
                for version in model['instances']:
                    new_models.append(model_to_be_added.copy())
                    new_models[-1]['timestamp'] = version['timestamp'][:19]
                    # inst['timestamp'][:19].replace(':','').replace(' ','').replace('-','')
                    
                    new_models[-1]['code_location'] = version['source']
                    new_models[-1]['version'] = version['version']
                    # we add the version-description to the description
                    new_models[-1]['description'] += '\n'+version['version']
                    
    print('number of models after update from Catalog: %i' % len(new_models))
    return new_models

    
if __name__=='__main__':

    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument("Protocol",
                        help="""
                        type of database update to be applied, choose between:
                        - 'Catalog-to-Local' 
                        - 'Catalog-to-Local-full-rewriting' (to restart from the CatalogDB)
                        - 'Local-to-Spreadsheet' 
                        - 'Spreadsheet-to-Local'
                        - 'Local-to-KG'
                        - 'KG-to-Local'
                        - 'SS-Release-Status'
                        """)
    args = parser.parse_args()

    if args.Protocol=='Fetch-Catalog':
        # N.B. the
        print('TO BE IMPLEMENTED (now relies on code living in the "hbp-validation-framework" repository)')
    if args.Protocol=='Catalog-to-Local':
        # read the Catalog DB and update the set of models
        models = from_catalog_to_local_db()
        # always make a backup copy before modifying the LocalDB
        local_db.create_a_backup_version(local_db.load_models())
        # then save the new version
        local_db.save_models_locally(models)
    if args.Protocol=='Catalog-to-Local-full-rewriting':
        # read the Catalog DB and update the set of models
        models = from_catalog_to_local_db(new_entries_only=False)
        # always make a backup copy before modifying the LocalDB
        # local_db.create_a_backup_version(local_db.load_models())
        # # then save the new version
        local_db.save_models_locally(models)
    if args.Protocol=='Local-to-Spreadsheet':
        # read the Catalog DB and update the set of models
        models = from_catalog_to_local_db()
        # always make a backup copy before modifying the LocalDB
        local_db.create_a_backup_version(local_db.load_models())
        # then save the new version
        local_db.save_models_locally(models)
        
    elif args.Protocol=='SS-to-Local':
        models = gsheet.read_from_spreadsheet(Range=[1,10000])
        print(len(models))

