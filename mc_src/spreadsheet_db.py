import pickle, os.path, string, sys, pathlib
import numpy as np

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from mc_src.model_template import template

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


Nkey_for_spreadsheet = 26 # number of keys from template shown in spreadsheet
KEYS_FOR_MODEL_ENTRIES = list(template.keys())[:Nkey_for_spreadsheet] #  the rest is private to LocalDB
# KEYS_FOR_MODEL_ENTRIES = [ # in the order you wish it to appear on the sheet !!
#     "alias", "owner", "name", "description", "author", "identifier", 
#     "versions", "code_location", "private",
#     "abstraction_level", "brain_region", "cell_type",
#     "creation_date", "license", "model_scope", "model_type",
#     "organization", "pla_components", "project",
#     "associated_dataset", "associated_method",
#     "associated_experimental_preparation", "used_software",
#     "code_format", "license", "parameters", "images"
# ]

KEYS_FOR_RELEASE_SUMMARY = ['Model alias', 'owner', 'in KG ?']+\
                           [key.replace('_', ' ')+' ?' for key in KEYS_FOR_MODEL_ENTRIES]+\
                           ['Total Score', 'Score for Release', 'Released ?']
Nkey_required_for_KG_release = 16 # number of keys from template used for the "Score for Release"


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
        

def get_raw_key_map(Sheet='Model Entries',
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
                          Sheet='Model Entries',
                          spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):
    """
    Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    sheet = initialize_gsheet()
    
    result = sheet.values().get(spreadsheetId=spreadsheetId,
                                range='%s!%i:%i' % (Sheet, Range[0], Range[1])).execute()
    values = result.get('values', [])

    models = [] # we read into a list of models

    if not values:
        print('No data found.')
        return []
    else:
        keys = values[0]
        for line in values[1:]:
            models.append({})
            for i, key in enumerate(keys):
                models[-1][key] = line[i]
        return models

def write_single_value_on_spreadsheet(value, key, line,
                                      Sheet='Model Entries',
                                      valueInputOption='USER_ENTERED', # USER_ENTERED or RAW
                                      spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):

    sheet = initialize_gsheet()
    result = sheet.values().update(
        spreadsheetId=spreadsheetId,
        range='%s!%s%i' % (Sheet, key, line),
        valueInputOption=valueInputOption, # USER_ENTERED or RAW
        body={'values': [[value]]}).execute()


def write_row_on_spreadsheet(values, row_letter, starting_index=1,
                             Sheet='Model Entries',
                             valueInputOption='USER_ENTERED', # USER_ENTERED or RAW
                             spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):
    sheet = initialize_gsheet()

    batch_update_values_request_body = {
        'value_input_option': valueInputOption,
        # The new values to apply to the spreadsheet.
        'data': [
            {
                'range':'%s!%s%i:%s%i' % (Sheet, row_letter, starting_index, row_letter, starting_index+len(values)),
                'values':[[v] for v in values],
            },
        ]
    }
    result = sheet.values().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=batch_update_values_request_body).execute()

def write_line_on_spreadsheet(values, line, starting_letter_index=0,
                              Sheet='Model Entries',
                              valueInputOption='USER_ENTERED', # USER_ENTERED or RAW
                              spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):
    sheet = initialize_gsheet()

    batch_update_values_request_body = {
        'value_input_option': valueInputOption,
        'data': []}
    for i in range(len(values)):
        batch_update_values_request_body['data'].append({
            'range':'%s!%s%i:%s%i' % (Sheet, get_alphabet_key(starting_letter_index+i), line, get_alphabet_key(starting_letter_index+i), line),
            'values':[[values[i]]],
            
        })
    result = sheet.values().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=batch_update_values_request_body).execute()


def write_DB_on_spreadsheet(values, line, starting_letter_index=0,
                            Sheet='Model Entries',
                            valueInputOption='USER_ENTERED', # USER_ENTERED or RAW
                            spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET']):
    sheet = initialize_gsheet()

    batch_update_values_request_body = {
        'value_input_option': valueInputOption,
        'data': []}
    for i in range(len(values)):
        batch_update_values_request_body['data'].append({
            'range':'%s!%s%i:%s%i' % (Sheet, get_alphabet_key(starting_letter_index+i), line, get_alphabet_key(starting_letter_index+i), line),
            'values':[[values[i]]],
            
        })
    result = sheet.values().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=batch_update_values_request_body).execute()
    


if __name__ == '__main__':

    if sys.argv[-1]=='write-spreadsheet-key':
        write_line_on_spreadsheet(KEYS_FOR_MODEL_ENTRIES, 1,
                                  Sheet='Model Entries')
        write_line_on_spreadsheet(KEYS_FOR_RELEASE_SUMMARY, 1,
                                  Sheet='KG Release Summary')
    else:
        print('debugging code:')

    # write_line_on_spreadsheet(KEYS_FOR_MODEL_ENTRIES, 1,
    #                           Sheet='Model Entries')
    # write_line_on_spreadsheet(KEYS_FOR_RELEASE_SUMMARY, 1,
    #                           Sheet='KG Release Summary')
    
    # print(read_from_spreadsheet(Range=[3,100],
    #                             Sheet='KG',
    #                             spreadsheetId=os.environ['MODEL_CURATION_SPREADSHEET_PREVIOUS']))
    # print(read_from_spreadsheet())
    # key_letter_map = get_raw_key_map()
    # write_single_value_on_spreadsheet('ntwk-Model-blabla', 'A', 2)
    # write_row_on_spreadsheet(range(10), 'C')
    # write_line_on_spreadsheet(range(10), 3)
    # write_line_entry_on_spreadsheet(['Model', 'Author'], 2, valueInputOption='RAW')
    # write_single_value_on_spreadsheet('Model Name', 'A network model about blabla', 2, key_letter_map)
    # write_single_value_on_spreadsheet('Custodian Name', 'Y. Zerlaut', 2, key_letter_map)
    # write_single_value_on_spreadsheet('Description', 1, 2, key_letter_map)
    # write_single_value_on_spreadsheet('Custodian Name', 'Y. Zerlaut', 2, key_letter_map)
    # write_single_value_on_spreadsheet('Custodian Name', 'Y. Zerlaut', 2, key_letter_map)
    # print(get_raw_key_labels())
    # import sys
    # sys.path.append('./')
    # from kg_interaction.fetch_models import get_list_of_models

    # model_list = get_list_of_models(10)
    # print(model_list)
    # write_on_spreadsheet()

