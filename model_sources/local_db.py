import sys, os, pathlib
import numpy as np
import pickle
print(pathlib.Path(__file__).resolve().parents[1])
sys.path.append(pathlib.Path(__file__).resolve().parents[1])
from processing.entries import refactor_model_entries
                
def save_models_locally(models):
    
    pkl_file = open(os.path.join(pathlib.Path(__file__).resolve().parent,
                                 'model_sources', 'LocalDB.pkl'),
                    'wb')
    pickle.dump(models, pkl_file)
    pkl_file.close()

def load_models():
    
    pkl_file = open(os.path.join(pathlib.Path(__file__).resolve().parent,
                                 'model_sources', 'LocalDB.pkl'),
                    'rb')

    models = pickle.load(pkl_file)
    pkl_file.close()
                
    return refactor_model_entries(models)

    
if __name__=='__main__':
    print(load_models())
