import sys, os

from model_sources import local_db, django_db
from spreadsheet import gsheet
from processing.entries import refactor_model_entries


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

    # print(gsheet.read_from_spreadsheet())
    
    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument("Protocol",
                        help="""
                        type of database update to be applied, choose between:
                        - 'Local-to-SS' 
                        - 'SS-to-Local'
                        - 'Local-to-KG'
                        - 'KG-to-Local'
                        - 'SS-Release-Status'
                        """)
    args = parser.parse_args()

    # if args.update_plot:
    #     data = dict(np.load(args.filename))
    #     data['plot'] = get_plotting_instructions()
    #     np.savez(args.filename, **data)
    # else:
    #     run()

    # print(gsheet.read_from_spreadsheet())
    print(args.DISTRIBUTION)
