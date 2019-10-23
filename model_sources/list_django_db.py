import sys, os
import numpy as np
import pickle

def get_models():
    pkl_file = open('Django_DB.pkl', 'rb')
    models = pickle.load(pkl_file)
    pkl_file.close()
    return models

if __name__=='__main__':
    print(get_models())

