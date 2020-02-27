import os, sys, pickle

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import gspread_formatting as gf

from fairgraph.client import KGClient
from fairgraph.uniminds import ModelInstance

KG_url_prefix = {'model':'https://kg.ebrains.eu/search/instances/Model/',
                 'dataset':'https://kg.ebrains.eu/search/instances/Dataset/',
                 'brain_structure':'', 'modelscope':'', 'study_target':'', # means no url links in KG
                 'custodian': 'https://kg.ebrains.eu/search/instances/Contributor/',
                 'contributor':'https://kg.ebrains.eu/search/instances/Contributor/'}


## 

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('service-account-credentials.json', scope)
gc = gspread.authorize(credentials)

sc = gc.open_by_url("https://docs.google.com/spreadsheets/d/%s/" % os.environ["SGA2_SP4_SPREADSHEET_ID"])

req_sheets = ['Signalling cascades', 'Inhibition and calcium cascades', 'Molecular Signalling Cascades' , 'Molecular Modelling', 'Multiscale', 'Human neurons', 'Basal ganglia', 'Cerebellum', 'Hippocampus', 'SSCx', 'Whole mouse brain']


COMPONENTS = {
    
    'Destexhe group':{'authors':['Destexhe, Alain']},
    
    'Einevoll group':{'authors':['Einevoll, Gaute', 'Ness, Torbjørn V.']},
}


if len(sys.argv)<2:
    print("""
    need to provide an argument, either: 
    - get-KG-released
    - Sheet
    - ANNEX-C
    - ANNEX-D
    """)

elif sys.argv[-1]=='get-KG-released':

    client = KGClient(os.environ['HBP_token'])
    models = ModelInstance.list(client, size=1000, api='query', scope='released', resolve=True)

    MODELS = {}

    for i, model in enumerate(models):
    
        print("%i) %s" % (i, model.name))
        MODELS[model.name] = {'url':KG_url_prefix['model']+model.identifier}

        for key in ['brain_structure', 'custodian', 'contributor', 'modelscope', 'study_target', 'custodian']:
            name = ''
            if getattr(model, key) is not None:
                if type(getattr(model, key)) is list:
                    for n in getattr(model, key):
                        name += n.resolve(client).name+'; '
                else:
                    name = getattr(model, key).resolve(client).name
                    MODELS[model.name][key+'_url'] = KG_url_prefix[key]+getattr(model, key).resolve(client).identifier
                print("  ---> %s: %s" % (key, name))
            MODELS[model.name][key] = name

        # Look for an associated dataset
        dataset = getattr(model, 'used_dataset')
        if dataset is not None:

            MODELS[model.name]['used_dataset'] = dataset.resolve(client).name
            MODELS[model.name]['dataset_url'] = KG_url_prefix['dataset']+dataset.resolve(client).identifier
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
            MODELS[model.name]['dataset_url'] = ''


    with open('db/SP4_KG_released.json', 'wb') as fout:
        pickle.dump(MODELS, fout)


elif sys.argv[-1]=='ANNEX-D':

    with open('db/SP4_KG_released.json', 'rb') as fout:
        MODELS = pickle.load(fout)

    lifecycle_col = 0 # A
    publication_col = 0 # A
    filter_col = 5 # F: Artefact Type
    output_sheet_name = "KG Models released - Annex D"

    # COLUMNS
    ouput_col_headings = ["Model Entry", "Custodian", "Associated Dataset", "Brain Region", "Species"]
    
    def build_str_array(name, model):
        # FUNCTION TO BUILD THE STRING CORRESPONDING TO THOSE COLUMNS
        dataset_string = '=HYPERLINK("%s","%s")' % (model['dataset_url'], model['used_dataset'])
        if ('molecular' in model['modelscope']) or ('subcellular' in model['modelscope']):
            dataset_string = 'sim. data stored and documented within model entry --> SGA3 for Simulation Datasets in KG!'
            
        return ['=HYPERLINK("%s","%s")' % (model['url'], name),
                '=HYPERLINK("%s","%s")' % (model['custodian_url'], model['custodian']),
                dataset_string,
                '%s' % model['brain_structure'],
                '%s' % model['dataset_species']]
    
    base_fontsize = 10

    req_data = []
    req_data_format = []
    blank_fmt = gf.cellFormat(
                            backgroundColor=gf.color(1,1,1),
                            textFormat=gf.textFormat(fontSize=base_fontsize, foregroundColor=gf.color(0,0,0))
                          )

    req_data.append(["Annex D: Models released in EBrains KG from SP4 Model Components"])
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
            if len(filters.keys())>1: # if not only authors, we check for other fields
                for key, val in filters.items():
                    if author_condition and (key!='authors') and model[key]==val: # this model fills the criteria
                        req_rows.append(build_str_array(name, model))
            elif author_condition: # author condition is enough
                req_rows.append(build_str_array(name, model))
                        
    
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
        params={'valueInputOption': 'USER_ENTERED'}, 
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

    
elif sys.argv[-1]=='Sheet':

    with open('db/SP4_KG_released.json', 'rb') as fout:
        MODELS = pickle.load(fout)

    output_sheet_name = "KG Models released"

    # COLUMNS
    ouput_col_headings = ["Model Entry", "Custodian", "Associated Dataset", "Brain Region", "Species"]
    
    def build_str_array(name, model):
        # FUNCTION TO BUILD THE STRING CORRESPONDING TO THOSE COLUMNS
        dataset_string = '=HYPERLINK("%s","%s")' % (model['dataset_url'], model['used_dataset'])
        if ('molecular' in model['modelscope']) or ('subcellular' in model['modelscope']):
            dataset_string = 'sim. data stored and documented within model entry --> SGA3 for Simulation Datasets in KG!'
            
        return ['=HYPERLINK("%s","%s")' % (model['url'], name),
                '=HYPERLINK("%s","%s")' % (model['custodian_url'], model['custodian']),
                dataset_string,
                '%s' % model['brain_structure'],
                '%s' % model['dataset_species']]
    
    base_fontsize = 10

    req_data = []
    req_data_format = []
    blank_fmt = gf.cellFormat(
                            backgroundColor=gf.color(1,1,1),
                            textFormat=gf.textFormat(fontSize=base_fontsize, foregroundColor=gf.color(0,0,0))
                          )

    req_data.append(["Models released in EBrains KG from SP4 Model Components"])
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
            if len(filters.keys())>1: # if not only authors, we check for other fields
                for key, val in filters.items():
                    if author_condition and (key!='authors') and model[key]==val: # this model fills the criteria
                        req_rows.append(build_str_array(name, model))
            elif author_condition: # author condition is enough
                req_rows.append(build_str_array(name, model))
                        
    
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
        params={'valueInputOption': 'USER_ENTERED'}, 
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
