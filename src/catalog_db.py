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
    

def add_version_details_to_model(minst_dict, minst_version, client):

    minst_dict['version'] = minst_version.version
    script = minst_version.main_script.resolve(client)
    minst_dict['code_format'] = (script.code_format, '')
    minst_dict['license'] = (script.license, '')
    try:
        minst_dict['code_location'] = (script.distribution.location, '')
    except AttributeError:
        minst_dict['code_location'] = ('', '')
        
    minst_dict['date_created'] = minst_version.timestamp
    minst_dict['version_description'] = minst_version.description
    minst_dict['modelvalidation_id'] = minst_version.id


def get_author_details(KG_author):

    return {'family_name':KG_author.family_name,
            'given_name':KG_author.given_name,
            'email':KG_author.email}
    
 
def load_model_instances(show_ignore=False,
                         size=100000,
                         # scope='inferred',
                         api='nexus'):

    client = KGClient(os.environ["HBP_token"])
    
    MODEL_INSTANCES = []

    models = ModelProject.list(client, api=api,
                               # scope=scope,
                               size=size)
    for model in models:
        minst = template.copy()
        minst['name'] = model.name
        minst['owner'] = get_author_details(model.owners.resolve(client))
        if type(model.authors) is list:
            minst['author(s)'] = [get_author_details(auth.resolve(client)) for auth in model.authors]
        else:
            minst['author(s)'] = [get_author_details(model.authors.resolve(client))]
        minst['description'] = model.description
        minst['private'] = model.private
        minst['collab_id'] = model.collab_id
        minst['alias'] = model.alias
        try:
            minst['organization'] = model.organization.resolve(client)
        except AttributeError:
            minst['organization'] = ''
        for key, quant in zip(['brain_region', 'species', 'celltype', 'abstraction_level', 'model_of'],
                              [model.brain_region, model.species, model.celltype, model.abstraction_level, model.model_of]):
            try:
                minst[key] = (quant.label, '')
            except AttributeError:
                minst[key] = ('', '')
        
        if type(model.instances) is list:
            for modelI in model.instances:
                MODEL_INSTANCES.append(minst.copy())
                add_version_details_to_model(MODEL_INSTANCES[-1], modelI.resolve(client), client)
        elif type(model.instances) is KGProxy:
            modelI = model.instances
            MODEL_INSTANCES.append(minst.copy())
            add_version_details_to_model(MODEL_INSTANCES[-1], modelI.resolve(client), client)
        elif show_ignore:
            print('Ignoring %s @ %s' % (model.name, model.date_created))
            pass # we don't care about models without specific version
        
    DATES = np.array([time.mktime(minst['date_created'].timetuple()) for minst in MODEL_INSTANCES])

    return [MODEL_INSTANCES[i] for i in np.argsort(DATES)[::-1]]


def show_list(models=None, show_ignore=False, show_ME=True,
              # scope='inferred',
              size=10000, api='query'):
    
    if models is None:
        models = load_model_instances(show_ignore=show_ignore, size=size,
                                      # scope=scope,
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

    # MODEL_INSTANCES = load_model_instances(show_ignore=True, size=100)
    # for i, minst in zip(range(len(MODEL_INSTANCES))[::-1], MODEL_INSTANCES[::-1]):
    #     print(i+1, ') ', minst.name.replace('ModelInstance for ', ''))

    from fairgraph.client import KGClient
    from fairgraph.brainsimulation import ModelProject, ModelInstance, use_namespace
    client = KGClient(os.environ["HBP_token"])
    MPs_Nexus = ModelProject.list(client, api="nexus", size=10000)
    N_Nexus = ModelProject.count(client, api="nexus")
    MPs_Query = ModelProject.list(client, api="query", scope='latest', size=10000)
    N_Query = ModelProject.count(client, api="query", scope='latest')
    print(len(MPs_Nexus))

    
    # show_list(show_ignore=True, show_ME=True, size=10000, api='nexus')#, scope='inferred')
    # show_list(show_ignore=True, show_ME=True, size=10000, api='nexus')
    # models = load_model_instances(show_ignore=False, size=10000)
    # import local_db
    # local_db.save_models(models)
    # pprint.pprint(models[1])
