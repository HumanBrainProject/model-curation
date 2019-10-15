import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('VF-DataSync-8e2e5296f1c5.json', scope)
gc = gspread.authorize(credentials)
sc = gc.open_by_url("https://docs.google.com/spreadsheets/d/1vOImr5ZJsus8HFVHK6OKmNXNN8mFQQTFQ59izPoNmQI/edit#gid=1434817642")

# Specify requirements
req_sheets = ['Signalling cascades', 'Inhibition and calcium cascades', 'Molecular Signalling Cascades' , 'Molecular Modelling', 'Multiscale', 'Human neurons', 'Basal ganglia', 'Cerebellum', 'Hippocampus', 'SSCx', 'Whole mouse brain']
lifecycle_col = 0 # A
publication_col = 0 # A
filter_col = 5 # F: Artefact Type
output_sheet_name = "Extracted Data - Annex B - New"
ouput_cols = [2, 17, 3, 0, -2, -1, 15] # in order: C, R, D, A, -2, -1, P
ouput_col_headings = ["Brain Region", "Species", "Cell Type", "Artefact Name", "Life Cycle Stage", "Publication", "Dissemination Status"]
base_fontsize = 10

req_data = []
req_data_format = []
blank_fmt = cellFormat(
                        backgroundColor=color(1,1,1),
                        textFormat=textFormat(fontSize=base_fontsize, foregroundColor=color(0,0,0))
                      )


req_data.append(["Annex B: Summary of Dissemination Status of SP6 SGA2 Model Components"])
fmt = cellFormat(
                    backgroundColor=color(1,1,1),
                    textFormat=textFormat(bold=True, fontSize=base_fontsize*2, foregroundColor=color(0.02,0.3,0.55))
                )
req_data_format.append(fmt)
req_data.append([""])
req_data_format.append(blank_fmt)

req_data.append(ouput_col_headings)
fmt = cellFormat(
                    backgroundColor=color(0.02,0.3,0.55),
                    textFormat=textFormat(bold=True, fontSize=base_fontsize, foregroundColor=color(1,1,1))
                )
req_data_format.append(fmt)

lifecycle = ""
publication = ""
for sheetname in req_sheets:
    worksheet = sc.worksheet(sheetname)
    # get all data as list of lists (each row is a list)
    worksheet_list = worksheet.get_all_values()
    req_rows = []
    for row in worksheet_list:
        if str(row[lifecycle_col]).lower() == "lifecycle stage":
            lifecycle = row[lifecycle_col+1]
        if str(row[publication_col]).lower() == "publication":
            publication = row[publication_col+1]
        if str(row[filter_col]).lower() == "model":
            row.extend([lifecycle, publication])
            req_rows.append([row[i] for i in ouput_cols])        
    print("{} -> {}".format(sheetname,len(req_rows)))
    req_data.append(["","","","","","",""])
    req_data_format.append(blank_fmt)
    req_data.append([sheetname,"","","","","",""])
    fmt = cellFormat(
                    backgroundColor=color(0.45,0.65,0.83),
                    textFormat=textFormat(bold=True, fontSize=base_fontsize+2, foregroundColor=color(0, 0, 0))
                )
    req_data_format.append(fmt)
    req_data.extend(req_rows)
    req_data_format.extend([blank_fmt]*len(req_rows))
    
try:    
    sc.del_worksheet(sc.worksheet(output_sheet_name))
except Exception:
    pass
worksheet = sc.add_worksheet(title=output_sheet_name, rows=len(req_data), cols=len(ouput_col_headings))
sc.values_update(
    '{}!A1'.format(output_sheet_name),
    params={'valueInputOption': 'RAW'}, 
    body={'values': req_data}
)

# to auto-resize the column widths
sheetId = sc.worksheet(output_sheet_name)._properties['sheetId']
body = {
    "requests": [
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheetId,
                    "dimension": "COLUMNS",
                    "startIndex": 0,  # Please set the column index.
                    "endIndex": len(ouput_col_headings)  # Please set the column index.
                }
            }
        }
    ]
}
res = sc.batch_update(body)

# to apply formatting to the cell contents: color, background, etc
for row in range(len(req_data)):
    if req_data_format[row] == blank_fmt: # temporary workaround to overcome google sheets API limit (100 requests per 100 seconds):
        continue
    format_cell_range(worksheet, rowcol_to_a1(row+1,1)+':' + rowcol_to_a1(row+1, len(ouput_col_headings)), req_data_format[row])
