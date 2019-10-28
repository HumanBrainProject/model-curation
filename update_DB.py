import sys, os

from model_sources import local_db, django_db
from spreadsheet import gsheet
from processing.entries import refactor_model_entries


if __name__=='__main__':

    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument("Protocol",
                        help="""
                        type of database update to be applied, choose between:
                        - 'Local-to-SS' 
                        - 'SS-to-Local'
                        - 'Local-to-KG'
                        - 'KG-to-Local'
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
