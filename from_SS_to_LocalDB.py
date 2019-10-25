from model_sources import local_db, django_db
from spreadsheet import gsheet



if __name__=='__main__':
    print(gsheet.read_from_spreadsheet())
