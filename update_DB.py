import sys, os, pprint, warnings, requests

from mc_src import local_db, catalog_db, KG_db, spreadsheet_db, model_template
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
        for ik, key in enumerate(['alias', 'owner', 'in_KG']):
            batch_update_values_request_body['data'].append({
                'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                          spreadsheet_db.get_alphabet_key(ik), 2+im,
                                          spreadsheet_db.get_alphabet_key(ik), 2+im),
            'values':[[reformat_for_spreadsheet(key, model[key])]]})
            
        ishift0 = ik+1
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
                                          spreadsheet_db.get_alphabet_key(ik+ishift0), 2+im,
                                          spreadsheet_db.get_alphabet_key(ik+ishift0), 2+im),
            'values':[[value]]})
        # Total count update
        batch_update_values_request_body['data'].append({
            'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                      spreadsheet_db.get_alphabet_key(ik+ishift0+1), 2+im,
                                      spreadsheet_db.get_alphabet_key(ik+ishift0+1), 2+im),
            'values':[[total_count]]})
        # Score for release update
        batch_update_values_request_body['data'].append({
            'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                      spreadsheet_db.get_alphabet_key(ik+ishift0+2), 2+im,
                                      spreadsheet_db.get_alphabet_key(ik+ishift0+2), 2+im),
            'values':[["%.2f" % release_count]]})
        # Release update
        batch_update_values_request_body['data'].append({
            'range':'%s!%s%i:%s%i' % ('KG Release Summary',
                                      spreadsheet_db.get_alphabet_key(ik+ishift0+3), 2+im,
                                      spreadsheet_db.get_alphabet_key(ik+ishift0+3), 2+im),
            'values':[[model['released_in_KG']]]})
            
    result = sheet.values().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=batch_update_values_request_body).execute()
    
def from_catalog_to_local_db(specific_id=[],
                             new_entries_only=True):

    models = catalog_db.load_models()

    if len(specific_id)>0:
        local_models = local_db.load_models()
        name_specific_ids = [local_models[i]['name'] for i in specific_id]
        name_previous_models, previous_models = [], []
        for m in models:
            if m['name'] not in name_specific_ids:
                name_previous_models.append(m['name'])
                previous_models.append(m)
    elif new_entries_only:
        previous_models = local_db.load_models()
        print('number of models before update from Catalog: %i' % len(previous_models))
        name_previous_models = [m['name'] for m in previous_models]
    else:
        previous_models, name_previous_models = [], []

    new_models = previous_models
    for model in models:
        # the Catalog DB can only update new entries to the DB
        if (model['name'] not in name_previous_models):
            print('-- ', model['name'])
            new_models.append(model)
    print('number of models after update from Catalog: %i' % len(new_models))
    return new_models


def check_KG_metadata_on_LocalDB(model, index):

    client = KG_db.KGClient(os.environ["HBP_token"])
    KG_db.check_authors_with_KG_entries(models[index], client) # Authors
    print(' ---- Other fields:')
    KG_db.check_fields_with_KG_entries(models[index], client)
    r = requests.get(models[index]['code_location'])
    if r.ok:
        print('[ok] The "code_location" seem to point to a valid url: '+models[index]['code_location'])
    else:
        print('[!!] The "code_location": %s is NOT a valid url: ' % models[index]['code_location'])
    
if __name__=='__main__':

    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument("Protocol",
                        help="""
                        type of database update to be applied, choose between:
                        - 'Fetch-Catalog'
                        - 'Catalog-to-Local'
                        - 'Check-Metadata'
                        - 'Local-to-Spreadsheet' 
                        - 'Local'
                        - 'Local-to-KG'
                        - 'KG-to-Local'
                        - 'Release-Summary'
                        """)
    parser.add_argument('-k', "--key", type=str,
                        help="key to be updated")
    parser.add_argument('-v', "--value", type=str, nargs='*',
                        help="value of the key to be updated")
    
    parser.add_argument('-sid', "--SheetID", type=int, default=0,
                        help="identifier of a model instance on the spreadsheet")
    parser.add_argument('-id', "--ID", type=int, default=-1,
                        help="identifier of a model instance")
    parser.add_argument('-idr', "--ID_range", type=str, default='',
                        help="range of identifier of model instances")
    parser.add_argument('-a', "--alias", type=str,
                        help="alias identifier of a model instance (as stated on the spreadsheet)")
    args = parser.parse_args()

    models = local_db.load_models()
    local_db.create_a_backup_version(models) # always create a backup version first

    # DEAL with MODEL ID
    if args.ID_range!='':
        try:
            ModelIDs = np.arange(int(args.ID_range.split('-')[0]),int(args.ID_range.split('-')[1])+1)
        except BaseException as e:
            print('\n ---> the range for sheet IDs needs to be of the form: "--ID_range 34-39"')
    elif args.ID>=0:
        ModelIDs = [args.ID-1] # ** -1 for indexes in LocalDB** 
    elif args.SheetID>=1:
        ModelIDs = [args.SheetID-2] # ** -2 for indexes in LocalDB**
    else:
        ModelIDs = []
        
    if args.Protocol=='Fetch-Catalog':
        catalog_models = catalog_db.load_model_instances(verbose=True)
        catalog_db.save_models(catalog_models)
        catalog_db.show_list(models=catalog_models)
    if args.Protocol=='Catalog-to-Local':
        models = from_catalog_to_local_db(specific_id=ModelIDs,
                                          new_entries_only=True)
        local_db.save_models(models)
    if args.Protocol=='Catalog-to-Local-full-rewriting':
        from_catalog_to_local_db(new_entries_only=False) # i.e. full rewriting
    if args.Protocol=='Local':
        models = local_db.load_models()
        for i in ModelIDs:
            if (args.key is not None) and (args.value is None):
                models[i][args.key] = KG_db.suggest_KG_entries_and_pick_one(models, i, args.key)
            elif args.key is not None:
                local_db.update_entry_manually(models, i, args)
            else:
                print('/!\ Need to provide a key and an updated value "--key name --value \'new name blabla\' "')
            print('New value for %s: \n   ' % args.key, models[i][args.key])
        local_db.save_models(models)
    if args.Protocol=='Check-Metadata':
        models = local_db.load_models()
        for i in ModelIDs:
            check_KG_metadata_on_LocalDB(models, i)
        local_db.save_models(models)
    if args.Protocol=='Local-to-Spreadsheet':
        models = local_db.load_models()
        from_local_db_to_spreadsheet(models)
        KG_db.add_KG_status_to_models(models) # KG & Release Status
        update_release_summary(models)
    if args.Protocol=='Release-Summary':
        models = local_db.load_models()
        KG_db.add_KG_status_to_models(models) # KG & Release Status
        update_release_summary(models)
        local_db.save_models(models)
    if args.Protocol=='Local-to-KG':
        models = local_db.load_models()
        for i in ModelIDs:
            KG_db.create_new_instance(models[i])
    if args.Protocol=='SS-to-Local':
        models = gsheet.read_from_spreadsheet(Range=[1,10000])
        print(len(models))

