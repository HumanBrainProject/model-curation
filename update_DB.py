import sys, os, pprint
import numpy as np

from model_sources import local_db, catalog_db, KG_db, spreadsheet_db
from spreadsheet import gsheet
from processing.entries import refactor_model_entries

# the template
from model_template import template

def from_catalog_to_local_db():

    models = catalog_db.load_models()

    previous_models = local_db.load_models()
    print('number of models before update from Catalog: %i' % len(previous_models))

    name_previous_models = [m['name'] for m in previous_models]
    new_models = previous_models
    
    for model in models:

        # the Catalog DB can only update new entries to the DB
        if model['name'] not in name_previous_models:
            
            new_models.append(template.copy())
            # dealing with the keys in common
            for key in template:
                if key in model:
                    new_models[-1][key] = model[key]
                if key=='creation_date':
                    new_models[-1][key] = model[key][:19]

            # then we look for the newest version
            if len(model['instances'])>0:
                instances = model['instances']
                timestamps = [int(inst['timestamp'][:19].replace(':','').replace(' ','').replace('-','')) for inst in instances]
                ilast_inst = np.argmax(np.array(timestamps))
                new_models[-1]['code_location'] = instances[ilast_inst]['source']
                new_models[-1]['version'] = instances[ilast_inst]['version']
                # we add the version-description to the description
                new_models[-1]['description'] += '\n'+instances[ilast_inst]['version']

    print('number of models before update from Catalog: %i' % len(new_models))
    return new_models

    
if __name__=='__main__':

    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument("Protocol",
                        help="""
                        type of database update to be applied, choose between:
                        - 'Catalog-to-Local' 
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

