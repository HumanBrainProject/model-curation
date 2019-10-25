import sys, os, pathlib
import numpy as np
import pickle

def save_models_locally():
    pkl_file = open(os.path.join(pathlib.Path(__file__).resolve().parent, 'model_sources', 'Local_DB.pkl'), 'rb')
    models = pickle.dump(pkl_file)
    pkl_file.close()

    for model in models:
        for key, val in model.items():
            if len(val.split('None'))>1:
                model[key] = 'None'
                
    return models

if __name__=='__main__':
    print(get_models())
