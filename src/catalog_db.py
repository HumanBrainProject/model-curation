import sys, os, pathlib
import numpy as np
import pickle, pprint
import time
import pprint

from fairgraph.client import KGClient
from fairgraph.base import KGProxy
from fairgraph.brainsimulation import ModelProject, ModelInstance, use_namespace

try:
    from .model_template import template
except ImportError:
    from model_template import template
    

def add_version_details_to_model(minst_dict, minst_version, client, verbose=False):

    minst_dict['version'] = minst_version.version
    script = minst_version.main_script.resolve(client)
    minst_dict['code_format'] = (script.code_format, '')
    minst_dict['license'] = (script.license, '')
    if script.distribution is not None:
        minst_dict['code_location'] = script.distribution.location
    elif verbose:
        print('[!!] "code_location" missing for %s ' % (minst_version.name))

    minst_dict['date_created'] = minst_version.timestamp
    minst_dict['version_description'] = minst_version.description
    minst_dict['modelvalidation_id'] = minst_version.id


def get_author_details(KG_author):

    return {'family_name':KG_author.family_name,
            'given_name':KG_author.given_name,
            'email':KG_author.email}
    
 
def load_model_instances(show_ignore=False,
                         size=100000,
                         scope='inferred',
                         verbose=False,
                         api='nexus'):

    client = KGClient(os.environ["HBP_token"])
    
    MODEL_INSTANCES = []

    models = ModelProject.list(client,
                               api=api,
                               scope=scope,
                               size=size)
        
    for model in models:

        if verbose:
            print('\n##########################################')
            print('------ %s ------' % model.name)
        minst = template.copy()
        minst['name'] = model.name

        minst['owner'] = get_author_details(model.owners.resolve(client))
        if type(model.authors) is list:
            minst['author(s)'] = [get_author_details(auth.resolve(client)) for auth in model.authors]
        else:
            minst['author(s)'] = [get_author_details(model.authors.resolve(client))]

        try:
            minst['authors_str'] = model.authors_str(client)
        except TypeError:
            minst['authors_str'] = ''
            for a in minst['author(s)']:
                minst['authors_str'] += a['family_name']+', '+a['given_name']+';' 

        minst['description'] = model.description
        minst['private'] = model.private
        minst['collab_id'] = model.collab_id
        minst['alias'] = model.alias

        for key, quant in zip(['brain_region', 'species', 'cell_type', 'abstraction_level', 'model_scope'],
                              [model.brain_region, model.species, model.celltype, model.abstraction_level, model.model_of]):
            if quant is not None:
                minst[key] = (quant.label, '')
            elif verbose:
                print('[!!] "%s" missing for %s ' % (key, model.name))
        for key, quant in zip(['organization'],
                              [model.organization]):
            if quant is not None:
                minst[key] = (quant.resolve(client).name, '')
            elif verbose:
                print('[!!] "%s" missing for %s ' % (key, model.name))

        if type(model.instances) is list:
            for modelI in model.instances:
                MODEL_INSTANCES.append(minst)
                # pprint.pprint(MODEL_INSTANCES[-1])
                # print('')
                add_version_details_to_model(MODEL_INSTANCES[-1], modelI.resolve(client), client, verbose=verbose)
        elif type(model.instances) is KGProxy:
            modelI = model.instances
            MODEL_INSTANCES.append(minst.copy())
            add_version_details_to_model(MODEL_INSTANCES[-1], modelI.resolve(client), client, verbose=verbose)
        elif show_ignore:
            print('Ignoring %s @ %s' % (model.name, model.date_created))
            pass # we don't care about models without specific version

        
    DATES = np.array([time.mktime(minst['date_created'].timetuple()) for minst in MODEL_INSTANCES])

    return [MODEL_INSTANCES[i] for i in np.argsort(DATES)[::-1]]


def show_list(models=None, show_ignore=False, show_ME=True,
              scope='inferred',
              size=10000, api='nexus'):
    
    if models is None:
        models = load_model_instances(show_ignore=show_ignore,
                                      size=size,
                                      scope=scope,
                                      api=api)

    for i, minst in zip(range(len(models))[::-1], models[::-1]):
        if (len(minst['name'].split('IGNORE'))==1) and (minst['name'] not in ['skjdfhskjdfh @ sadf', 'lkfjgldkfgj @ sfdgdfg', 'lkfjgldkfgj @']) and (len(minst['name'].split('MEModel'))==1 or show_ME):
            print(i+1, ') ', minst['name'].replace('ModelInstance for ', ''))
            
            
def show_entry(model):

    for key, val in model.items():
        if key=='author(s)':
            names  = ''
            for auth in val:
                names += '%s, %s ; ' % (auth.family_name, auth.given_name)
            print('- %s : %s' % (key, names[:-2]))
        elif key=='owner':
            print('- %s : %s' % (key, '%s, %s ; ' % (val.family_name, val.given_name)))
        else:
            print('- %s : %s' % (key, val))
    

def load_models(filename=None):
    """ """
    if filename is None:
        filename = os.path.join(pathlib.Path(__file__).resolve().parents[1],
                                'db', 'CatalogDB.pkl')
    pkl_file = open(filename, 'rb')
    models = pickle.load(pkl_file)
    pkl_file.close()
    
    # we sort them by creation date (the last one is the newest)
    dates = np.array([time.mktime(minst['date_created'].timetuple()) for minst in models])
    return [models[i] for i in np.argsort(dates)[::-1]]

def save_models(models):
    """ """
    pkl_file = open(os.path.join(pathlib.Path(__file__).resolve().parents[1],
                                 'db', 'CatalogDB.pkl'), 'wb')
    pickle.dump(models, pkl_file)
    pkl_file.close()
            
if __name__=='__main__':
    
    # models = load_models(client)

    MODEL_INSTANCES = load_model_instances(show_ignore=True, size=30, api='nexus', scope='inferred', verbose=True)
    pprint.pprint(MODEL_INSTANCES)
    # for i, minst in zip(range(len(MODEL_INSTANCES))[::-1], MODEL_INSTANCES[::-1]):
    #     print(i+1, ') ', minst.name.replace('ModelInstance for ', ''))

    # from fairgraph.client import KGClient
    # from fairgraph.brainsimulation import ModelProject, ModelInstance, use_namespace
    # client = KGClient(os.environ["HBP_token"])
    # MPs_Nexus = ModelProject.list(client, api="nexus", size=10000)
    # N_Nexus = ModelProject.count(client, api="nexus")
    # MPs_Query = ModelProject.list(client, api="query", scope='latest', size=10000)
    # N_Query = ModelProject.count(client, api="query", scope='latest')
    # print(len(MPs_Nexus))
    
    # show_list(show_ignore=True, show_ME=True, size=10000, api='nexus')#, scope='inferred')
    # show_list(show_ignore=True, show_ME=True, size=10000, api='nexus')
    # models = load_model_instances(show_ignore=False, size=10000)
    # import local_db
    # local_db.save_models(models)
    # pprint.pprint(models[1])

    """
    client = KGClient(os.environ["HBP_token"])
    models = ModelProject.list(client, api='nexus',
                                size=1)

    KEYWORD = ' '
    for model in models:
        if len(model.name.split(KEYWORD))>1:
            print(model)
            if type(model.authors) is list:
                for author in model.authors:
                    print(author.resolve(client))
            else:
                print(model.authors.resolve(client))
            print(model.name, '\n')

    models = ModelInstance.list(client, api='nexus',
                                size=1)
    for model in models:
        if len(model.name.split(KEYWORD))>1:
            print(model.name)
            print(model)
            print(model.main_script.resolve(client).distribution.location)
            print(model.main_script.resolve(client), '\n')
    """
