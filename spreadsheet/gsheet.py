import pickle, os.path
import numpy as np

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def initialize_gsheet():

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    
    return sheet

def write_author_names():

    sheet = initialize_gsheet()
    
def read_from_spreadsheet(n=1000):

    # The ID and range of a sample spreadsheet.
    # SAMPLE_RANGE_NAME = 'Model_entries!1:10'
    SAMPLE_RANGE_NAME = 'Model_entries!1:%i' % n

    
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    
    sheet = initialize_gsheet()
    
    result = sheet.values().get(spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET'],
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    Models_dict = {}
    for key in values[0]:
        Models_dict[key] = []

    if not values:
        print('No data found.')
    else:
        for row in values[1:]:
            for i, key in enumerate(values[0]):
                try:
                    print(i, key, row[i])
                    Models_dict[key].append(row[i])
                    print('-->', Models_dict[key])
                except IndexError:
                    print(i, key)
                    Models_dict[key].append('')
                
    return Models_dict


if __name__ == '__main__':
    # print(read_from_spreadsheet(10))
    # main()
    # write_author_names()

