import sys, os

from model_sources import local_db, django_db
from spreadsheet import gsheet
from processing.entries import refactor_model_entries


    
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

    if args.Protocol=='SS-to-Local':
        models = gsheet.read_from_spreadsheet(Range=[1,10000])
        print(len(models
))

