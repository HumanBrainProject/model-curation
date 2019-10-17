import pickle, os.path, string
import numpy as np

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    
    return sheet

def get_alphabet_key(index):
    if index<len(string.ascii_uppercase):
        return string.ascii_uppercase[index]
    else:
        return string.ascii_uppercase[int(index/len(string.ascii_uppercase))-1]+string.ascii_uppercase[index%len(string.ascii_uppercase)]
        
def get_raw_key_map(Sheet='Model_entries',
                    spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):
    """
    Get top values from the spreadsheet
    """
    sheet = initialize_gsheet()
    result = sheet.values().get(spreadsheetId=spreadsheetId,
                                range='%s!1:1' % Sheet).execute()
    key_letter_map = {}
    for i, key in enumerate(result.get('values')[0]):
        key_letter_map[key] = get_alphabet_key(i)
        
    return key_letter_map


def read_from_spreadsheet(Range=[1,2],
                          Sheet='Model_entries',
                          spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    sheet = initialize_gsheet()
    
    result = sheet.values().get(spreadsheetId=spreadsheetId,
                                range='%s!%i:%i' % (Sheet, Range[0], Range[1])).execute()
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

def write_single_value_on_spreadsheet(key, value, line,
                                      key_letter_map,
                                      Sheet='Model_entries',
                                      valueInputOption='USER_ENTERED', # USER_ENTERED or RAW
                                      spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):

    sheet = initialize_gsheet()
    result = sheet.values().update(
        spreadsheetId=spreadsheetId,
        range='%s!%s%i' % (Sheet, key_letter_map[key], line),
        valueInputOption=valueInputOption, # USER_ENTERED or RAW
        body={'values': [[value]]}).execute()


def write_line_entry_on_spreadsheet(values, line,
                                    key_letter_map,
                                    Sheet='Model_entries',
                                    valueInputOption='USER_ENTERED', # USER_ENTERED or RAW
                                    spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):

    sheet = initialize_gsheet()
    result = sheet.values().update(
        spreadsheetId=spreadsheetId,
        range='%s!%i' % (Sheet, line),
        valueInputOption=valueInputOption, # USER_ENTERED or RAW
        body={'values': [[Model_dict[key_letter_map[i]] for i in range(len(key_letter_map.keys()))]]}).execute()
    

if __name__ == '__main__':
    # print(read_from_spreadsheet(Range=[3,100],
    #                             Sheet='KG',
    #                             spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET_PREVIOUS']))
    # print(read_from_spreadsheet())
    key_letter_map = get_raw_key_map()
    write_single_value_on_spreadsheet('Model Alias', 'ntwk-Model-blabla', 2, key_letter_map)
    write_single_value_on_spreadsheet('Model Name', 'A network model about blabla', 2, key_letter_map)
    write_single_value_on_spreadsheet('Custodian Name', 'Y. Zerlaut', 2, key_letter_map)
    write_single_value_on_spreadsheet('Description', 1, 2, key_letter_map)
    write_single_value_on_spreadsheet('Custodian Name', 'Y. Zerlaut', 2, key_letter_map)
    write_single_value_on_spreadsheet('Custodian Name', 'Y. Zerlaut', 2, key_letter_map)
    # print(get_raw_key_labels())
    # import sys
    # sys.path.append('./')
    # from kg_interaction.fetch_models import get_list_of_models

    # model_list = get_list_of_models(10)
    # print(model_list)
    # write_on_spreadsheet()

