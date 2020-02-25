import os, sys, pathlib, numpy
from fairgraph.client import KGClient
from fairgraph.uniminds import Person, BrainStructure, CellularTarget, License, ModelFormat, ModelInstance, ModelScope, Publication, StudyTarget, FileBundle, Organization, Dataset, AbstractionLevel

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from processing import emails, names
import hashlib, pprint

def add_KG_status_to_models(models):
    """
    Checking if models:
    1) appear as KG entries
    2) are released in the KG (using the scope='released' filter to fetch released entries in the KG)
    """

    print('Checking models status in KG [...]')
    model_names = numpy.array([m['name'] for m in models], dtype=str) # all model names of LocalDB

    #### MODELS IN KG ####
    KGmodels_all = ModelInstance.list(client, api='query',
                                           scope='inferred',
                                           size=len(models))
    count = 0
    for model in KGmodels_all: # looping over released KG models
        In_catalog = False
        iSmodel = numpy.argwhere(model_names==model.name).flatten()
        for imodel in iSmodel: # looping over LocalDB versions for a given model !
            if (models[imodel]['version']==model.version) or (model.name+'_'+models[imodel]['version']==model.version):
                models[imodel]['in_KG'] = 'True'
                count+=1
                In_catalog = True
            models[imodel]['KG_identifier'], models[imodel]['KG_id'] = str(model.identifier), str(model.id)
        if not In_catalog:
            if len(iSmodel)==1:
                print('For the model:', model.name)
                print('  ---> the version names didnt match between KG and Catalog so we change it to the KG one:', model.version, 'instead of', models[imodel]['version'])
                models[imodel]['version'] = model.version
                models[imodel]['KG_identifier'], models[imodel]['KG_id'] = str(model.identifier), str(model.id)
                count+=1
            else:
                print(model.name, 'not found in the Catalog DB')
                print('the available versions are:')
                print('In the Knowledge graph :', model.version)
                print('In the Model Catalog :', [models[imodel]['version'] for imodel in iSmodel])

    
    #### RELEASED MODELS IN KG ####
    KGmodels_released = ModelInstance.list(client, api='query',
                                           scope='released',
                                           size=len(models))

    model_names = numpy.array([m['name'] for m in models], dtype=str)
    count = 0
    for model in KGmodels_released: # looping of released KG models
        In_catalog = False
        iSmodel = numpy.argwhere(model_names==model.name).flatten()
        for imodel in iSmodel: # looping over LocalDB versions for a given model !
            if models[imodel]['version']==model.version:
                models[imodel]['released_in_KG'] = 'True'
                count+=1
                In_catalog = True
            models[imodel]['KG_identifier'], models[imodel]['KG_id'] = str(model.identifier), str(model.id)
        if not In_catalog:
            if len(iSmodel)==1:
                print('For the model:', model.name)
                print('  ---> the version names didnt match between KG and Catalog so we change it to the KG one:', model.version, 'instead of', models[imodel]['version'])
                models[imodel]['version'] = model.version
                models[imodel]['KG_identifier'], models[imodel]['KG_id'] = str(model.identifier), str(model.id)
                count+=1
            else:
                print(model.name, 'not found in the Catalog DB')
                print('the available versions are:')
                print('In the Knowledge graph :', model.version)
                print('In the Model Catalog :', [models[imodel]['version'] for imodel in iSmodel])
        
    print('Checking release status in KG --> Done ! (%i models published in the KG)' % count)
    return models


def fetch_models(api='query', scope='inferred', n=100000):

    client = KGClient(os.environ["HBP_token"])
    if api is 'nexus':
        KGmodels = ModelInstance.list(client, api=api, size=n, resolved=True)
    else:
        KGmodels = ModelInstance.list(client, api=api, size=n, resolved=True, scope=scope)

    models = []
    for m in KGmodels:
        models.append({})
        for key, val in m.__dict__.items():
            if (type(val) is str) or (type(val) is list):
                models[-1][key] = val
            elif key=='instance' or (val is None):
                models[-1][key] = str(val)
            else:
                try:
                    models[-1][key] = val.name
                except AttributeError:
                    print(key)
    return models

def get_model_attributes(client):
    KGmodels = ModelInstance.list(client, api="query", resolved=True, size=1)
    return KGmodels[0].__dict__.keys()


def find_person_in_KG(full_name, client, ask=False):

    name_decompositions = [full_name]
    # name_decompositions = [full_name,
    #                        full_name.split(',')[-1],
    #                        full_name.split(',')[0],
    #                        full_name.split('.')[-1],
    #                        full_name.split('.')[0]]
    Persons, KGid_Persons, Emails = [], [], []
    for name in name_decompositions:
        person = Person.by_name(name, client, api='query')
        if person is not None:
            if person.identifier not in KGid_Persons:
                KGid_Persons.append(person.identifier)
                Persons.append('%s, %s' % (person.family_name, person.given_name))
                Emails.append(person.email)
                
    person = ("", "") # by default
    if ask:
        print('------------------------------')
        if len(Persons)>0:
            print('Potentially matching authors:')
            for i, name in enumerate(Persons):
                print(' %i) %s, %s' % (i, Persons[i], Emails[i]))

            try:
                iperson = int(input('Pick the index of the matching person [enter, to skip]: '))
                if iperson in range(len(Persons)):
                    person = (Persons[iperson], KGid_Persons[iperson])
            except (ValueError, TypeError):
                pass

        if person[0] is "":
            print('/!\ NO matching authors: Go to the KG Editor and manually insert:')
            print('        ', full_name, ' as a uniminds.Person entry !')
        else:
            print('Person set to: ', Persons[iperson])

        return person
    else:
        if len(Persons)==1:
            print('[ok] %s, %s was found in the KG' % (Persons[0], Emails[0]))
            return (Persons[0], KGid_Persons[0])
        elif len(Persons)>1:
            print('[!!] multiple persons were found for %s' % full_name)
            print(Persons)
            return ("", "")
        else:
            print('[!!] %s was NOT found in the KG' % full_name)
            return ("", "")
        

def check_authors_with_KG_entries(model, client):
    """
    """

    success_flag = True
    if 'owner_str' not in model:
        try:
            model['owner_str'] = model['owner']['family_name']+', '+model['owner']['given_name']
        except TypeError:
            model['owner_str'] = model['owner'][0]
    print(' ---- Owner: (based on "owner_str": %s )' % model['owner_str'])
            
    model['owner'] = find_person_in_KG(model['owner_str'], client)
    print(' ---- Authors: (based on "authors_str" %s )' % model['authors_str'])
    Author_list = model['authors_str'].split(';')
    model['author(s)'] = [] # reinitialized
    for author in Author_list:
        auth = find_person_in_KG(author, client)
        if auth[0] is "":
            success_flag = False
        model['author(s)'].append(auth)
    return success_flag


def find_entry_in_KG(name, cls, client):
    """
    a cleaner version should be built based on the "exists" function of KG classes
    """

    entry_name = cls.by_name(name=name, client=client, api='query', resolved=True)
    try:
        entry_uuid = cls.by_uuid(name, client=client, api='query', resolved=True, scope='inferred')
    except AttributeError:
        entry_uuid = None
    try:
        entry_id = cls.by_id(name, client=client, api='query', resolved=True, scope='inferred')
    except AttributeError:
        entry_id = None
        
    if entry_name is not None:
        print('[ok] The entry "%s" was found in the KG as a %s' % (name, cls))
        return (entry_name.name, entry_name.uuid)
    elif entry_id is not None:
        print('[ok] The entry "%s" was found in the KG as a %s' % (name, cls))
        return (entry_id.name, entry_id.uuid)
    elif entry_uuid is not None:
        print('[ok] The entry "%s" was found in the KG as a %s' % (name, cls))
        return (entry_uuid.name, entry_uuid.uuid)
    else:
        try:
            list_of_all_entries = cls.list(client, api='query', scope='released', size=100000)
            names = numpy.array([entry.name for entry in list_of_all_entries], dtype=str)
            uuids = numpy.array([entry.uuid for entry in list_of_all_entries], dtype=str)
            iSmodel = numpy.argwhere(names==name).flatten()

            if len(iSmodel)>0:
                print('[ok] The entry "%s" was found in the KG as a %s' % (name, cls))
                return (name, uuids[iSmodel[0]])
            else:
                print('[!] The entry "%s" for the %s was *NOT* found in the KG' % (name, cls))
                return (name,'')
        except ValueError:
            print('[!] The entry "%s" for the %s was *NOT* found in the KG' % (name, cls))
            return (name,'')

        
def check_fields_with_KG_entries(model, client):
    """
    """
    
    for key, cls in zip(['abstraction_level', 'brain_region', 'cell_type', 'license',
                         'code_format', 'model_scope', 'organization'],
                        [AbstractionLevel, BrainStructure, CellularTarget, License, ModelFormat, ModelScope, Organization]):
        model[key] = find_entry_in_KG(model[key][0], cls, client)

    for key, cls in zip(['associated_dataset'],
                        [Dataset]):
        
        for elem in model[key]:
            elem = find_entry_in_KG(str(elem[0]), cls, client)
        

def suggest_KG_entries_and_pick_one(models, i, desired_key):
    """
    """
    client = KGClient(os.environ["HBP_token"])

    print('\nHere is the list of available entries for that entity:')
    for key, cls in zip(['abstraction_level', 'brain_region', 'cell_type', 'license',
                         'code_format', 'model_scope'],
                        [AbstractionLevel, BrainStructure, CellularTarget, License, ModelFormat, ModelScope]):
        if key==desired_key:
            KEY_LIST = cls.list(client, size=10000, api='query', resolve=True, scope='released')
            for i, k in enumerate(KEY_LIST):
                print(' - %i) %s' % (i, k.name))
    print('\nHere is the list of available entries for that entity:')
    print('/!\ if that entry is not available in the list, create it in the KG-editor and release it /!\ ')
    values = input('\nDo you want to add one ? (use either "3", or "2,3,4" or "2,58,3", ...)\n')
    value_list = values.split(',')
    if (len(value_list)==1) and (value_list[0]==''):
        return models[i][desired_key]
    elif len(value_list)==1:
        return (KEY_LIST[int(value_list[0])].name,
                KEY_LIST[int(value_list[0])].identifier)
    else:
        OUTPUT = []
        for value in value_list:
            OUTPUT.append((KEY_LIST[int(value)].name,
                           KEY_LIST[int(value)].identifier))
        return OUTPUT

    
def create_new_instance(model):

    prerequisite_ok = True # switch to false below if not

    # check
    for key in ['owner', 'abstraction_level', 'brain_region', 'cell_type',
                'license', 'code_format', 'model_scope']:
        if model[key][1]=='':
            prerequisite_ok = False
            print('Need to fetch the UUID of the entry "%s" for the key "%s" ' %\
                  (model[key][0], key))
    for author in model['author(s)']:
        if author[1]=='':
            prerequisite_ok = False
            print('Need to fetch the UUID of the author "%s" ' % author[0])
    if model['code_location']=='':
        prerequisite_ok = False
        print('no code location')

    
    if not prerequisite_ok:
        print('===========================================================')
        print('  the entry *can not* be pushed to the Knowledge Graph')
        print('            fix the metadata first')
        print('===========================================================')
    else:
        pprint.pprint(model)
        print('===========================================================')
        print('  the entry *can* be pushed to the Knowledge Graph')
        print('    please review the above information carefully')
        print('===========================================================')

    if input('are you sure that the above informations are correct ? y/[n]\n') in ['y', 'yes']:
        client = KGClient(os.environ["HBP_token"])

        custodian = Person.by_name(model['owner'][0], client, api='query')
        list_of_authors = [Person.by_name(auth[0], client, api='query')\
                           for auth in model['author(s)']]

        al = AbstractionLevel.from_uuid(model['abstraction_level'][1], client, api='query')
        bs = BrainStructure.from_uuid(model['brain_region'][1], client, api='query')
        ct = CellularTarget.from_uuid(model['cell_type'][1], client, api='query')
        lic = License.from_uuid(model['license'][1], client, api='query')
        mf = ModelFormat.from_uuid(model['code_format'][1], client, api='query')
        ms = ModelScope.from_uuid(model['model_scope'][1], client, api='query')

        UUID = hashlib.md5("{} @ {}".format(model['name'],model['version']).encode('utf-8')).hexdigest()
        minst = ModelInstance(name=model['name'],
                              version=model['version'],
                              abstraction_level=al,
                              brain_structure=bs,
                              cellular_target=ct,
                              model_format=mf,
                              model_scope=ms,
                              license=lic,
                              description=model['description'],
                              custodian = custodian,
                              contributor = list_of_authors,
                              identifier=UUID)

        minst.save(client)
        print('[ok] created the ModelInstance')
        
        minst = ModelInstance.by_name(model['name'], client, api='query')
        if minst is not None:

            name = 'filebundle for the code of %s @ %s' % (model['name'], model['version'])
            fb = FileBundle(name=name,
                            description = 'file bundle for model '+name,
                            identifier=hashlib.sha1(name.encode('utf-8')).hexdigest(),
                            url=model['code_location'],
                            model_instance = minst)
            try:
                fb.save(client)
                print('[ok] created the FileBundle')
            except BaseException as e:
                print('------------- ERROR --------------------')
                print(e)
                print('------------- ERROR --------------------')
                print('Need to manually create the FileBundle:')
                print('- name:', name)
                print('- description:', name)
                print('- identifier:', hashlib.sha1(name.encode('utf-8')).hexdigest())
                print('- url:', model['code_location'])
                print('- model_instance:', minst.name)
            
        else:
            print('Model instance not found !')
            print('KG update takes some time, retry later...')
            
        
def from_modelvalidation_to_uniminds(model):

    prerequisite_ok = True # switch to false below if not

    pprint.pprint(model)
    print('===========================================================')
    print('  the entry *can* be pushed to the Knowledge Graph')
    print('    please review the above information carefully')
    print('===========================================================')

    client = KGClient(os.environ["HBP_token"])

    # print(model['owner'])
    # custodian = Person.by_name(model['owner'].family_name+', '+model['owner'].given_name,
    #                            client, api='query', scope='inferred')
    # print(custodian)
    list_of_authors = [Person.from_uuid(auth.family_name+', '+auth.given_name, client) for auth in model['author(s)']]

    # al = AbstractionLevel.from_uuid(model['abstraction_level'][1], client, api='query')
    # bs = BrainStructure.from_uuid(model['brain_region'][1], client, api='query')
    # ct = CellularTarget.from_uuid(model['cell_type'][1], client, api='query')
    # lic = License.from_uuid(model['license'][1], client, api='query')
    # cf = ModelFormat.from_uuid(model['code_format'][1], client, api='query')

    # full_minst_name = model['name']+' '+model['version']
    # minst = ModelInstance(name=model['name'],
    #                       identifier=hashlib.sha1(full_minst_name.encode('utf-8')).hexdigest(),
    #                       description=model['description'],
    #                       main_contact = custodian,
    #                       version=model['version'],
    #                       abstraction_level = al,
    #                       brain_structure = bs,
    #                       cellular_target = ct,
    #                       license = lic,
    #                       modelformat = cf,
    #                       custodian = custodian,
    #                       contributor = list_of_authors)

    # minst.save(client)
    #     print('[ok] created the ModelInstance')

    #     try:
    #         minst = ModelInstance.by_name(model['name'], client)

    #         name = 'filebundle for the code of %s @ %s' % (model['name'], model['version'])
    #         fb = FileBundle(name=name,
    #                         description = 'file bundle for model '+name,
    #                         identifier=hashlib.sha1(name.encode('utf-8')).hexdigest(),
    #                         url=model['code_location'],
    #                         model_instance = minst)
    #         try:
    #             fb.save(client)
    #             print('[ok] created the FileBundle')
    #         except BaseException as e:
    #             print('------------- ERROR --------------------')
    #             print(e)
    #             print('------------- ERROR --------------------')
    #             print('Need to manually create the FileBundle:')
    #             print('- name:', name)
    #             print('- description:', name)
    #             print('- identifier:', hashlib.sha1(name.encode('utf-8')).hexdigest())
    #             print('- url:', model['code_location'])
    #             print('- model_instance:', minst.name)
            
    #     except BaseException as e:
    #         print(e)
    #         print('Model instance not found !')
    #         print('KG update takes some time, retry later...')
            
        
            
    
if __name__ == '__main__':

    client = KGClient()

    print(ModelInstance.from_id('c3862631-1905-4375-b477-699e94f5f6ea', client))
    
    # for model in Dataset.list(client, api='query', scope='inferred', size=100):
    #     print(model)
    
    # print(AbstractionLevel.from_uuid('33cd7f9e-0f6e-46af-8a55-1e3fbebbb0f0', client))
    
    # from src import local_db
    # models = local_db.load_models()
    # for m in models[11:15]:
    #     print('-------------------------------')
    #     for author in m['author(s)']:
    #         first_name, last_name = names.resolve_name(author[0])
    #         print(get_or_create_person_in_KG(first_name, last_name, client, os.environ["HBP_token"]))
    #         # person = Person()
    #         # print(person.by_name(last_name+', '+first_name, client))
    #         # print(author[0], person.exists(client))
    #         # print(emails.get_email(first_name, last_name, os.environ["HBP_token"]))
    #         # person = Person(name=last_name+', '+first_name)












