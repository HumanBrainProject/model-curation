from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '18baJz2Vup_zUpNoi7-ugc-kz-AHZqP2wCxq3wvvrsmw'
SAMPLE_RANGE_NAME = 'Model_entries!1:10'

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


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    
    sheet = initialize_gsheet()
    
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print(row)

if __name__ == '__main__':
    main()

# spreadsheet_id = '1mr2Lt8dogAlWNp3tfR-c2Z1LLNdeNYuUJEivI3wfGV0'

# requests = []
# # Change the spreadsheet's title.
# requests.append({
#     'updateSpreadsheetProperties': {
#         'properties': {
#             'title': 'Models'
#         },
#         'fields': 'title'
#     }
# })
# # Find and replace text
# requests.append({
#     'findReplace': {
#         'find': 0,
#         'replacement': 1,
#         'allSheets': True
#     }
# })
# # Add additional requests (operations) ...

# body = {
#     'requests': requests
# }
# response = service.spreadsheets().batchUpdate(
#     spreadsheetId=spreadsheet_id,
#     body=body).execute()
# find_replace_response = response.get('replies')[1].get('findReplace')
# print('{0} replacements made.'.format(
#     find_replace_response.get('occurrencesChanged')))
