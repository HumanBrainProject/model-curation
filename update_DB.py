import sys, os, pprint
import numpy as np

from src import local_db, catalog_db, KG_db, spreadsheet_db, model_template
from processing.entries import reformat_from_catalog, reformat_for_spreadsheet, reformat_date_to_timestamp, find_meaningfull_alias, version_naming, concatenate_words


def from_local_db_to_spreadsheet(models,
                                 valueInputOption='USER_ENTERED', # USER_ENTERED or RAW
                                 spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):
    """
    see details about the Google Spreadsheet API in the 'src/spreadsheet_db.py' code
    """
    sheet = spreadsheet_db.initialize_gsheet()

    batch_update_values_request_body = {
        'value_input_option': valueInputOption,
        'data': []}

    for im, model in enumerate(models):
        for ik, key in enumerate(spreadsheet_db.KEYS_FOR_MODEL_ENTRIES):
            batch_update_values_request_body['data'].append({
                'range':'%s!%s%i:%s%i' % ('Model Entries',
                                          spreadsheet_db.get_alphabet_key(ik),
                                          2+im,
                                          spreadsheet_db.get_alphabet_key(ik),
                                          2+im),
            'values':[[reformat_for_spreadsheet(key, model[key])]],
            })
    result = sheet.values().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=batch_update_values_request_body).execute()

def update_release_summary(models,
                           valueInputOption='USER_ENTERED', # USER_ENTERED or RAW
                           spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):
    """
    see details about the Google Spreadsheet API in the src/spreadsheet_db.py code
    """
    sheet = spreadsheet_db.initialize_gsheet()

    batch_update_values_request_body = {
        'value_input_option': valueInputOption,
        'data': []}

    for im, model in enumerate(models):
        # writing the alias and owner
        for ik, key in enumerate(['alias', 'owner']):
            batch_update_values_request_body['data'].append({
                'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                          spreadsheet_db.get_alphabet_key(ik), 2+im,
                                          spreadsheet_db.get_alphabet_key(ik), 2+im),
            'values':[[reformat_for_spreadsheet(key, model[key])]]})
        # checking if keys are present...
        total_count, release_count = 0, 0
        for ik, key in enumerate(spreadsheet_db.KEYS_FOR_MODEL_ENTRIES):
            value = 0
            if reformat_for_spreadsheet(key, model[key]) not in ['', 'None', 'False']:
                value = 1
                total_count +=1
                if ik<spreadsheet_db.Nkey_required_for_KG_release:
                    release_count += 1./spreadsheet_db.Nkey_required_for_KG_release
            batch_update_values_request_body['data'].append({
                'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                          spreadsheet_db.get_alphabet_key(ik+2), 2+im,
                                          spreadsheet_db.get_alphabet_key(ik+2), 2+im),
            'values':[[value]]})
        # Total count update
        batch_update_values_request_body['data'].append({
            'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                      spreadsheet_db.get_alphabet_key(ik+3), 2+im,
                                      spreadsheet_db.get_alphabet_key(ik+3), 2+im),
            'values':[[total_count]]})
        # Score for release update
        batch_update_values_request_body['data'].append({
            'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                      spreadsheet_db.get_alphabet_key(ik+4), 2+im,
                                      spreadsheet_db.get_alphabet_key(ik+4), 2+im),
            'values':[["%.2f" % release_count]]})
        # Release update
        batch_update_values_request_body['data'].append({
            'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                      spreadsheet_db.get_alphabet_key(ik+5), 2+im,
                                      spreadsheet_db.get_alphabet_key(ik+5), 2+im),
            'values':[[model['released_in_KG']]]})
            
    result = sheet.values().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=batch_update_values_request_body).execute()
    

def from_catalog_to_local_db(new_entries_only=True):

    models = catalog_db.load_models()

    if new_entries_only:
        previous_models = local_db.load_models()
        print('number of models before update from Catalog: %i' % len(previous_models))
        name_previous_models = [m['name'] for m in previous_models]
    else:
        previous_models = [] # no previous models to fully rewrite the DB
        name_previous_models = []
    
    new_models = previous_models
    
    for model in models:

        # the Catalog DB can only update new entries to the DB
        if (model['name'] not in name_previous_models):

            model_to_be_added = model_template.template.copy()
            # dealing with the keys in common
            for key, val in model_template.template.items():
                if key=='author(s)':
                    model_to_be_added['author(s)'] = reformat_from_catalog(key, val, model['author'])
                elif key=='public':
                    if model['private']=='False':
                        model_to_be_added['public'] = 'True'
                elif key=='model_type':
                    model_to_be_added[key] = reformat_from_catalog(key, val, model[key])
                    print(model_to_be_added[key])
                elif key in model:
                    model_to_be_added[key] = reformat_from_catalog(key, val, model[key])
                if key=='model_type':
                    print(model['name'], model_to_be_added[key])

            if model_to_be_added['owner'][0] in ['', 'None']:
                model_to_be_added['owner'] = model_to_be_added['author(s)'][0]
            
            if len(model['instances'])==0: # if no version, we add a fake one at submission data
                model['instances'].append({'version':'None',
                                           'id':'', 'parameters':'',
                                           'source':'', 'description':'',
                                           'timestamp':model_to_be_added['creation_date']})

            # looping over versions
            for version in model['instances']:
                new_models.append(model_to_be_added.copy())
                new_models[-1]['timestamp'] = reformat_date_to_timestamp(version['timestamp'])
                # inst['timestamp'][:19].replace(':','').replace(' ','').replace('-','')
                new_models[-1]['code_location'] = version['source']
                new_models[-1]['version'] = version['version']
                # we add the version-description to the description
                new_models[-1]['description'] += '\n'+version['version']
                # parameters
                new_models[-1]['parameters'] = version['parameters']
                new_models[-1]['identifier'] = version['id']

                # let's insure that we have a proper alias
                if new_models[-1]['alias'] in ['', 'None']:
                    new_models[-1]['alias'] = find_meaningfull_alias(new_models[-1]['name'])
                elif len(new_models[-1]['alias'].split(' '))>1:
                    new_models[-1]['alias'] = concatenate_words(new_models[-1]['alias'].split(' '))
                # and add the version 
                new_models[-1]['alias'] += ' @ '+version_naming(version['version'])
                print(new_models[-1]['model_type'])#[0] = 'Type'
                    
    print('number of models after update from Catalog: %i' % len(new_models))
    return new_models

def add_KG_metadata_to_LocalDB(models):

    models = KG_db.add_release_status_to_models(models) # Release Status
    
if __name__=='__main__':

    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument("Protocol",
                        help="""
                        type of database update to be applied, choose between:
                        - 'Catalog-to-Local' 
                        - 'Catalog-to-Local-full-rewriting' (to restart from the CatalogDB)
                        - 'Add-KG-Metadata-to-Local'
                        - 'Local-to-Spreadsheet' 
                        - 'Spreadsheet-to-Local'
                        - 'Local-to-KG'
                        - 'KG-to-Local'
                        - 'Release-Summary'
                        """)
    args = parser.parse_args()

    if args.Protocol=='Fetch-Catalog':
        # N.B. the
        print('TO BE IMPLEMENTED (now relies on code living in the "hbp-validation-framework" repository)')
    if args.Protocol=='Catalog-to-Local':
        local_db.create_a_backup_version(local_db.load_models())
        # read the Catalog DB and update the set of models
        models = from_catalog_to_local_db()
        # always make a backup copy before modifying the LocalDB
        # then save the new version
        local_db.save_models_locally(models)
    if args.Protocol=='Catalog-to-Local-full-rewriting':
        # read the Catalog DB and update the set of models
        models = from_catalog_to_local_db(new_entries_only=False)
        # always make a backup copy before modifying the LocalDB
        # local_db.create_a_backup_version(local_db.load_models())
        # # then save the new version
        local_db.save_models_locally(models)
    if args.Protocol=='Add-KG-Metadata-to-Local':
        models = local_db.load_models()
        local_db.create_a_backup_version(models)
        models = add_KG_metadata_to_LocalDB(models)
        local_db.save_models_locally(models)
    if args.Protocol=='Local-to-Spreadsheet':
        models = local_db.load_models()
        from_local_db_to_spreadsheet(models)
    if args.Protocol=='Release-Summary':
        models = local_db.load_models()
        update_release_summary(models)
    elif args.Protocol=='SS-to-Local':
        models = gsheet.read_from_spreadsheet(Range=[1,10000])
        print(len(models))

