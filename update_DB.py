import sys, os, pprint, warnings

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
                elif key in model:
                    model_to_be_added[key] = reformat_from_catalog(key, val, model[key])

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
                new_models[-1]['description'] += '\nversion: '+version['version']
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
                    
    print('number of models after update from Catalog: %i' % len(new_models))
    return new_models

def add_KG_metadata_to_LocalDB(model, index):
    print(' === FETCHING METADATA FROM KG TO ADD TO LOCAL DB === ')
    print(' ---- Authors:')
    KG_db.replace_authors_with_KG_entries(models[index]) # Authors
    print(' ---- Other fields:')
    KG_db.replace_fields_with_KG_entries(models[index])            

def update_entry_manually(model, args):

    if (args.key in model) and args.value is not None:
        if type(model[args.key]) is tuple:
            if input('Do you want to replace the value "%s" for key "%s" by: "%s" ? y/[n]\n' % (model[args.key][0], args.key, args.value[0])) in ['y', 'yes']:
                model[args.key] = (args.value[0], '')
                print('[ok] value changed to', model[args.key])
            else:
                print('[!!] value not changed')
        elif type(model[args.key]) is list:
            if input('Do you want to replace the value "%s" for key "%s" by: "%s" ? y/[n]\n' % (model[args.key], args.key, args.value)) in ['y', 'yes']:
                model[args.key] = []
                print(args.value)
                for elem in args.value:
                    model[args.key].append((elem, ''))
                print('[ok] value changed to', model[args.key])
            else:
                print('[!!] value not changed')
    elif (args.key in model):
        print('The value for key %s is currently: %s' % (args.key, model[args.key]))
    else:
        pprint.pprint(model)
        print('[!!] key not found')
    
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
                        - 'Local'
                        - 'Local-to-KG'
                        - 'KG-to-Local'
                        - 'Release-Summary'
                        """)
    parser.add_argument('-k', "--key", type=str, help="key to be updated")
    parser.add_argument('-v', "--value", type=str, nargs='*',
                        help="value of the key to be updated")
    
    parser.add_argument('-sid', "--SheetID", type=int, default=-1,
                        help="identifier of a model instance on the spreadsheet")
    parser.add_argument('-sidr', "--SheetID_range", type=str, default='',
                        help="identifier of a model instance on the spreadsheet")
    parser.add_argument('-a', "--alias", type=str,
                        help="alias identifier of a model instance (as stated on the spreadsheet)")
    args = parser.parse_args()

    models = local_db.load_models()
    local_db.create_a_backup_version(models) # always create a backup version first

    ModelIDs = []
    if args.SheetID_range!='':
        try:
            ModelIDs = np.arange(int(args.SheetID_range.split('-')[0]),int(args.SheetID_range.split('-')[1])+1)-2 # ** -2 for indexes in LocalDB** 
        except BaseException as e:
            print('\n ---> the range for sheet IDs needs to be of the form: "--SheetID_range 34-39"')
    elif args.SheetID>1:
        ModelIDs = [args.SheetID-2] # ** -2 for indexes in LocalDB** 
    elif args.Protocol in ['Local', 'Add-KG-Metadata-to-Local', 'Local-to-KG']:
        print('Need to specify a model identifier as a Google Sheet index (i.e. *>=2*, e.g. with "--SheetID 3")')

        
    if args.Protocol=='Fetch-Catalog':
        # backing up the previous database
        os.system('mv db/Django_DB.pkl db/backups/Django_DB.pkl')
        path = '/home/yzerlaut/work/hbp-validation-framework'
        validation_path = os.path.join(path, 'validation_service')
        command_path = os.path.join(path, 'model_validation_api', 'management', 'commands')
        os.system('cp src/django_db.py '+str(os.path.join(command_path, 'get_django_db.py')))
        os.system('cd '+str(validation_path)+'; python manage.py get_django_db')
        os.system('mv '+os.path.join(validation_path, 'Django_DB.pkl')+' db/')
        print('[ok] Database succesfully moved to "db/" folder (Django_DB.pkl)')
    if args.Protocol=='Catalog-to-Local':
        # read the Catalog DB and update the set of models
        models = from_catalog_to_local_db()
        # then save the new version
        local_db.save_models(models)
    if args.Protocol=='Catalog-to-Local-full-rewriting':
        models = from_catalog_to_local_db(new_entries_only=False)
        local_db.save_models(models)
    if args.Protocol=='Local':
        local_db.create_a_backup_version(local_db.load_models())
        models = local_db.load_models()
        for i in ModelIDs:
            update_entry_manually(models[i], args)
            print(models[i][args.key])
        local_db.save_models(models)
    if args.Protocol=='Add-KG-Metadata-to-Local':
        models = local_db.load_models()
        local_db.create_a_backup_version(models)
        for i in ModelIDs:
            add_KG_metadata_to_LocalDB(models, i)
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

