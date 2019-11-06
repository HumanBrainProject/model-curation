import sys, os, pathlib
from datetime import datetime
import numpy as np
import pickle
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from processing.entries import refactor_model_entries


def create_a_backup_version(models):
    """
    create a backup pkl datafile in the "local_db_backups" directory
    """
    pkl_file = open(os.path.join(str(pathlib.Path(__file__).resolve().parents[0]),
                                 'backups_local_db',
                                 datetime.now().strftime("%Y.%m.%d-%H:%M:%S.pkl")), 'wb')
    pickle.dump(models, pkl_file)
    pkl_file.close()


def save_models_locally(models):
    """ """
    pkl_file = open(os.path.join(pathlib.Path(__file__).resolve().parents[0],
                                 'LocalDB.pkl'), 'wb')

    # forcing the elements with possible KG entries to be of the form:
    for model in models:
        for key in model:
            if type(model[key]) is list:
                for ie, elem in enumerate(model[key]):
                    if elem is not tuple:
                        model[key][ie] = (elem,"")
            else:
                if type(model[key]) is not tuple:
                    model[key] = (model[key],"")
                    
    pickle.dump(models, pkl_file)
    pkl_file.close()

    
def load_models(filename=None):
    """ """
    if filename is None:
        filename = os.path.join(pathlib.Path(__file__).resolve().parents[0],
                                'LocalDB.pkl')
    pkl_file = open(filename, 'rb')
    Models = pickle.load(pkl_file)
    pkl_file.close()
                
    models = refactor_model_entries(Models)
    # we sort them by creation date (the last one is the newest)
    dates = np.array([int(model['creation_date']) for model in models])
    return [models[i] for i in np.argsort(dates)[::-1]]

def get_model_attributes():
    models = load_models()
    return models[0].keys()


if __name__=='__main__':
    # create_a_backup_version(load_models())
    models = load_models()
    save_models_locally(models)
    # print(models[4].keys())
    # print(models[4]['author'])
                            
