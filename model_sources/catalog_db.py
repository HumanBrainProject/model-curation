import sys, os, pathlib
import numpy as np
import pickle, pprint

def load_models():
    pkl_file = open(os.path.join(pathlib.Path(__file__).resolve().parent,'CatalogDB.pkl'), 'rb')
    models = pickle.load(pkl_file)
    pkl_file.close()

    # for model in models:
    #     model['author'] = model['author'].replace(',', ';')
    #     # for key, val in model.items():
    #     #     if len(val.split('None'))>1:
    #     #         model[key] = 'None'
                
    return models

# here we store a list of models that were tests and wree not intended to be released
SET_OF_EXCEPTIONS = [
    'fs_morphologies',
    'str-fs-161205_FS1-BE37A-20180212',
    'msn_d2_all-5-20170517',
    '',
]

if __name__=='__main__':
    models = load_models()
    for model in models:
        print('----------------------------------------')
        print('- %s ' % model['name'])
        print('  * %s' % model['description'])
