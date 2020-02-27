import os, sys, pickle

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import gspread_formatting as gf

from fairgraph.client import KGClient
from fairgraph.uniminds import ModelInstance


## 

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('service-account-credentials.json', scope)
gc = gspread.authorize(credentials)

sc = gc.open_by_url("https://docs.google.com/spreadsheets/d/%s/" % os.environ["SGA2_SP6_SPREADSHEET_ID"])

req_sheets = ['Signalling cascades', 'Inhibition and calcium cascades', 'Molecular Signalling Cascades' , 'Molecular Modelling', 'Multiscale', 'Human neurons', 'Basal ganglia', 'Cerebellum', 'Hippocampus', 'SSCx', 'Whole mouse brain']


COMPONENTS = {
    'Signalling cascades':{'modelscope':'subcellular',
                           'authors':['Kramer, Andrei', 'Tewatia, Parul', 'Eriksson, Olivia']},
    'Inhibition and calcium cascades':{'modelscope':'', # TO BE FILLED
                                       'authors':['Kramer, Andrei', 'Hellgren Kotaleski, Jeanette', 'Eriksson, Olivia', 'Serna, Pablo', 'Triller, Antoine']},
    'Molecular Signalling Cascades':{'modelscope':'subcellular: molecular',
                                     'authors':['Bruce, Neil', 'Narzi, Daniele', 'Hellgren Kotaleski, Jeanette']},
    'Molecular Modelling':{'modelscope':'subcellular: molecular',
                           'authors':['Bruce, Neil', 'Capelli, Riccardo', 'Kokh, Daria']},
    'Multiscale':{'brain_structure':'striatum',
                  'authors':['Bruce, Neil', 'Capelli, Riccardo', 'Kokh, Daria']},
    'Human neurons':{'brain_structure':'cerebral cortex',
                     'authors':['Eyal, Guy']},
    'Basal ganglia':{'brain_structure':'basal ganglia',
                     'authors':['Lindroos, Robert', 'Kozlov, Alexander', 'Johansson, Yvonne', 'Frost Nylen, Johanna']},
    'Cerebellum':{'brain_structure':'cerebellum',
                  'authors':['Masoli, Stefano', 'Rizza, Martina', 'Tognolina, Marialuisa', 'Locatelli, Francesca',
                             'Nedelescu, Hermina', 'Muñoz, Alberto', 'Gagliano, Giuseppe', 'Geminiani, Alice', 'Casellato, Claudia','Soda, Teresa']},
    'Hippocampus':{'brain_structure':'hippocampus',
                   'authors':['Romandi, Armando']},
    'SSCx':{'brain_structure':'somatosensory cortex',
            'authors':['Alonso, Lidia', 'Merchan Perez, Angel', 'BBP-team']},
    'Whole mouse brain':{'brain_structure':'whole brain',
                         'authors':['Csaba, Eroe', 'Dimitri, Rodarie']}
}



if len(sys.argv)<2:
    print("""
    need to provide an argument, either: 
    - 
    - 
    - 
    """)

elif sys.argv[-1]=='get-KG-released':

    client = KGClient(os.environ['HBP_token'])
    models = ModelInstance.list(client, size=1000, api='query', scope='released', resolve=True)

    MODELS = {}

    for i, model in enumerate(models):
    
        print("%i) %s" % (i, model.name))
        MODELS[model.name] = {}

        for key in ['brain_structure', 'custodian', 'contributor', 'modelscope', 'study_target', 'custodian']:
            name = ''
            if getattr(model, key) is not None:
                if type(getattr(model, key)) is list:
                    for n in getattr(model, key):
                        name += n.resolve(client).name+'; '
                else:
                    name = getattr(model, key).resolve(client).name
                print("  ---> %s: %s" % (key, name))
            MODELS[model.name][key] = name

        # Look for an associated dataset
        dataset = getattr(model, 'used_dataset')
        if dataset is not None:

            MODELS[model.name]['used_dataset'] = dataset.resolve(client).name
            sg = dataset.resolve(client).specimen_group
            if type(sg) is list:
                sg = sg[0] # just the first elements is enough (hoping there is no more than 1 species per dataset)
            subject = sg.resolve(client).subjects
            if type(subject) is list:
                subject = subject[0] # just the first elements is enough (hoping there is no more than 1 species per specimengroup)
            MODELS[model.name]['dataset_species'] = subject.resolve(client).species.resolve(client).name
            print("  ---> %s: %s" % ('dataset_species', MODELS[model.name]['dataset_species']))

        else:
            MODELS[model.name]['used_dataset'] = ''
            MODELS[model.name]['dataset_species'] = ''


    with open('db/SP6_KG_released.json', 'wb') as fout:
        pickle.dump(MODELS, fout)


elif sys.argv[-1]=='ANNEX-D':

    with open('db/SP6_KG_released.json', 'rb') as fout:
        MODELS = pickle.load(fout)

    lifecycle_col = 0 # A
    publication_col = 0 # A
    filter_col = 5 # F: Artefact Type
    output_sheet_name = "KG Models (curated) - Annex D"

    ouput_col_headings = ["Model Name", "Custodian", "Associated Dataset", "Brain Region", "Species"]
    base_fontsize = 10

    req_data = []
    req_data_format = []
    blank_fmt = gf.cellFormat(
                            backgroundColor=gf.color(1,1,1),
                            textFormat=gf.textFormat(fontSize=base_fontsize, foregroundColor=gf.color(0,0,0))
                          )

    req_data.append(["Annex D: Models released in EBrains KG from SP6 SGA2 Model Components"])
    fmt = gf.cellFormat(
                        backgroundColor=gf.color(1,1,1),
                        textFormat=gf.textFormat(bold=True, fontSize=base_fontsize*2, foregroundColor=gf.color(0.02,0.3,0.55))
                    )
    req_data_format.append(fmt)
    req_data.append([""])
    req_data_format.append(blank_fmt)

    req_data.append(ouput_col_headings)
    fmt = gf.cellFormat(
                        backgroundColor=gf.color(0.02,0.3,0.55),
                        textFormat=gf.textFormat(bold=True, fontSize=base_fontsize, foregroundColor=gf.color(1,1,1))
                    )
    req_data_format.append(fmt)

    for sheetname, filters in COMPONENTS.items():
        req_rows = []
        # find models that match the filters
        for name, model in MODELS.items():

            # first the author condition
            author_condition = False
            for author in filters['authors']:
                if author in model['contributor']:
                    author_condition = True
                    
            # then the other filters
            for key, val in filters.items():
                if author_condition and (key!='authors') and model[key]==val: # this model fills the criteria
                    req_rows.append([name]+[model[k] for k in ['custodian', 'used_dataset', 'brain_structure', 'dataset_species']])
                    
        print("{} -> {}".format(sheetname,len(req_rows)))
        req_data.append(["","","","","","",""])
        req_data_format.append(blank_fmt)
        req_data.append([sheetname,"","","","","",""])
        fmt = gf.cellFormat(
                        backgroundColor=gf.color(0.45,0.65,0.83),
                        textFormat=gf.textFormat(bold=True, fontSize=base_fontsize+2, foregroundColor=gf.color(0, 0, 0))
                    )
        req_data_format.append(fmt)
        req_data.extend(req_rows)
        req_data_format.extend([blank_fmt]*len(req_rows))
                
    req_data.append(["","","","","","",""])
    req_data_format.append(blank_fmt)
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
        gf.format_cell_range(worksheet, gspread.utils.rowcol_to_a1(row+1,1)+':' + gspread.utils.rowcol_to_a1(row+1, len(ouput_col_headings)), req_data_format[row])


    
elif sys.argv[-1]=='ANNEX-B':

    
    lifecycle_col = 0 # A
    publication_col = 0 # A
    filter_col = 5 # F: Artefact Type
    output_sheet_name = "Extracted Data - Annex B - New"
    ouput_cols = [2, 17, 3, 0, -2, -1, 15] # in order: C, R, D, A, -2, -1, P
    ouput_col_headings = ["Brain Region", "Species", "Cell Type", "Artefact Name", "Life Cycle Stage", "Publication", "Dissemination Status"]
    base_fontsize = 10

    req_data = []
    req_data_format = []
    blank_fmt = gf.cellFormat(
                            backgroundColor=gf.color(1,1,1),
                            textFormat=gf.textFormat(fontSize=base_fontsize, foregroundColor=gf.color(0,0,0))
                          )


    req_data.append(["Annex B: Summary of Dissemination Status of SP6 SGA2 Model Components"])
    fmt = gf.cellFormat(
                        backgroundColor=gf.color(1,1,1),
                        textFormat=gf.textFormat(bold=True, fontSize=base_fontsize*2, foregroundColor=gf.color(0.02,0.3,0.55))
                    )
    req_data_format.append(fmt)
    req_data.append([""])
    req_data_format.append(blank_fmt)

    req_data.append(ouput_col_headings)
    fmt = gf.cellFormat(
                        backgroundColor=gf.color(0.02,0.3,0.55),
                        textFormat=gf.textFormat(bold=True, fontSize=base_fontsize, foregroundColor=gf.color(1,1,1))
                    )
    req_data_format.append(fmt)

    lifecycle = ""
    publication = ""
    for sheetname in COMPONENTS.keys():
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
        fmt = gf.cellFormat(
                        backgroundColor=gf.color(0.45,0.65,0.83),
                        textFormat=gf.textFormat(bold=True, fontSize=base_fontsize+2, foregroundColor=gf.color(0, 0, 0))
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
        gf.format_cell_range(worksheet, gspread.utils.rowcol_to_a1(row+1,1)+':' + gspread.utils.rowcol_to_a1(row+1, len(ouput_col_headings)), req_data_format[row])


