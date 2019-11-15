# Model curation process

A python module for the model curation process in the HBP. 

It details the pipeline applied to /Model/ entries from their submission in the [Model Catalog](https://collab.humanbrainproject.eu/#/collab/19/nav/369318?state=model.n) (by the HBP contributors) to their publications in the [EBRAINS Knowledge Graph Search](https://kg.ebrains.eu/search). 

## Model curation in context

Model curation consists in making the release of models comply with the [FAIR](https://www.go-fair.org/fair-principles/) principles of data sharing (Findability, Accessibility, Interoperability, Reusability).

The curation process includes automatic processes of database updates together with manual editing of entries in Google Spreadsheets and email/tickets interactions with the model contributors.

## Schematic of the curation pipeline

![process](docs/process.png)

We detail below the different steps composing the curation pipeline

## Installation and environment setup
### Installing dependencies

Two python modules of the Human Brain Project ecosystem:

- [[https://github.com/HumanBrainProject/fairgraph][fairgraph]]: A high-level Python API for the HBP Knowledge Graph
- [[https://github.com/HumanBrainProject/hbp-validation-client][hbp-validation-client]]: A Python package for working with the Human Brain Project Model Validation Framework.
- [[https://github.com/HumanBrainProject/hbp-validation-client][hbp-validation-framework]]: A Python package for working with the Human Brain Project Model Validation Framework.

The Python API for working with Google Spreadsheets:

- [[https://developers.google.com/sheets/api][Google Spreadsheet API]]

Follow the instructions to get the credentials at:

https://developers.google.com/sheets/api/quickstart/python

### Installing the `model-curation` module

Clone the repository:

```
git clone https://github.com/yzerlaut/model-curation.git
```

### Setting up your environmment

Fill the following file with appropriate informations related to you installation
```
import os

# location of your json files for the HBP logins
hbp_token_file=os.path.join(os.path.expanduser("~"), "Downloads", "HBP.json")
hbp_storage_token_file=os.path.join(os.path.expanduser("~"), "Downloads", "config.json")

# location of your hbp-validation-framework repository
validation_framework_path = os.path.join(os.path.expanduser("~"), "work", "hbp_validation_framework")
# credentials required to fetch informations from the PostgreSQL database of the Model Catalog
VALIDATION_FRAMEWORK_INFOS = {    
    "DJANGO_SECRET_KEY":"'...'",
    "HBP_OIDC_CLIENT_ID":"...",
    "HBP_OIDC_CLIENT_ID":"...",
    "HBP_OIDC_CLIENT_SECRET":"...",
    "HBP_OIDC_CLIENT_SECRET":"...",
    "VALIDATION_SERVICE_PASSWORD":"...",
    "VALIDATION_SERVICE_HOST":"...",
    "VALIDATION_SERVICE_PORT":"...",
}

# ID of Google Spreadsheets
SPREADSHEETS_ID = {
    "MODEL_CURATION_SPREADSHEET":"...",
    "MODEL_CURATION_SPREADSHEET_PREVIOUS":"...",
    "SGA2_SP6_SPREADSHEET_ID" :"...",
    "SGA2_SP3_SPREADSHEET_ID" : "...",
}
```

*## Environment (loading necessary bash variables)

run the =setting_env_variables.sh=  script in the shell 

```
cd folder_where_you_have_cloned_the_repo/model-curation/
source setting_env_variables.sh
``` 

This should output something like:
```
-----TOKENS -------------------
[ok] the new HBP token is eyJhbGciOi...uH41znzh-Y
[ok] the new CSCS token is eyJhbGciOi...QYRSFb_sSg
-----SPREADSHEET -------------------
[ok] MODEL_CURATION_SPREADSHEET
[ok] MODEL_CURATION_SPREADSHEET_PREVIOUS
[ok] SGA2_SP6_SPREADSHEET_ID
[ok] SGA2_SP3_SPREADSHEET_ID
-----VALIDATION FRAMEWORK INFOS -------------------
[ok] DJANGO_SECRET_KEY
[ok] HBP_OIDC_CLIENT_ID
[ok] HBP_OIDC_CLIENT_SECRET
[ok] VALIDATION_SERVICE_PASSWORD
[ok] VALIDATION_SERVICE_HOST
[ok] VALIDATION_SERVICE_PORT
``` 


## Curation steps

### 1) Fetching data from the Model Catalog app

Steps performed: 

- We fetch the informations from the PostgreSQL database of the Model Catalog app, with:

- We transform the "model-based" set of entries in the Model Catalog to a "version-based" set of entries.

- We search in the Knowledge Graph for the UUID (thanks to =fairgraph=) of the provided entries of all fields in the model (when possible). We associate all entries to this =UUID= in the local database).


Those are performed in two steps:

```
python update_DB.py Fetch-Catalog
```

The update of the Local database from the updated Catalog information is made with:
```
python update_DB.py Catalog-to-Local
```

Note that this only happens new models to the Local database, it doesn't rewrite the full local database. If you want to (re)-start from scratch from the information contained in the Model Catalog, use:
```
python update_DB.py Catalog-to-DB-full-rewriting
```

If you want to restart from scratch while keeping your manual updates of the entries (i.e. the modifications resulting from the interactions with the users done in *Step 5*) **TO BE IMPLEMENTED**
```
python update_DB.py Catalog-to-DB-full-rewriting-with-stored-changes
```

N.B. If the model is released in the KG and the "version name" does not match any of the version name found in the Catalog. Assuming that their is only one version (what is the case), for the "version name" in the LocalDB, we take the one of the KG not of the Catalog. This only happens for this set of models: (https://kg.ebrains.eu/search/?q=granule&facet_type[0]=Contributor#Contributor/2c916596118aa1ae6070497dae75dda2)

### 2) Writing the local DB on the spreadsheet

```
python update_DB.py Local-to-Spreadsheet
```

### 3) Visualize information

See the spreadsheet. You can get this url by typing in the shell:

```
echo $curation_url
```

(this was loaded by the =setting_env_variables.sh= script)

### 4) Interact with model producers to fix missing fields

Done through emails or [[https://support.humanbrainproject.eu/#ticket/view/my_tickets][Zammad platform]]

### 5) Update the entries

Fix missing information, ...

### 6) Writing the spreadsheet updates on the Local DB

```
python update_DB Spreadsheet-to-Local
```

- At that step again, we search in the Knowledge Graph for the UUID (thanks to =fairgraph=) of the provided entries of all fields in the model (when possible). We associate all entries to this =UUID= in the local database).

### 7) Write to KG

- *Other KG consistency check needed*

```
python update_DB Local-to-KG
```

### 8) Release models in the KG

If a model passes all criteria and the authors wants it to be published. Go the [[https://kg-editor.humanbrainproject.eu/][Knowledge Graph Editor]], search for the desired entry using the "filter" tool. Use the "release" button (shape of a cloud) to release the model.

## Rationale behind the pipeline

*## Transformation from a "model-based" set of entries (in the Model Catalog) to a "version-based" set of entries

The Model Catalog database considers entries which are conceptual models that can have evolving implementation over time. On the other hand, the Knowledge Graph only considers specific model instances with a well-defined implementation that can be potentially released (and therefore should be [[https://www.go-fair.org/fair-principles/][FAIR]]).

The chosen approach therefore duplicates a model across all its versions in the Knowledge Graph. A model with 10 versions in the Model Catalog will therefore have 10 ModelInstances in the Knowledge Graph.

*## Use of a local DB and editing through the Google Spreadsheet

The central database of the pipeline is the local databsae and not the Google Spreadsheet (what could be possible, one would store all data on the Spreadsheet and modify directly from there). The reason for this choice is that this service might disappear or become broken. In that case, another tool could be set up to interact and modify the LocalDb. A command line tool will be available soon (*TO BE DONE*).

Also, having the local database allows simple backups over time (in charge of the curator).

## Model template

The metadata are stored as a tuple of strings (=name=, =UUID=), where =name= is a string identifyin the entry and =UUID= is the Knowledge graph identifier the name . Either "free" strings or strings corresponding to the UUID in the Knowledge Graph (e.g. the metadata related to the Person =Yann Zerlaut= has the UUID: =003beed8-1ee8-45ec-8737-785ca6239ef0=).

An empty template is stored in the =model_template.py= file. It reads:
```
template = {
    
    # Note that the order matters (it used for display in the Spreadsheets)
    "alias":"", # a string
    
    "version":"", # a string
    
    "owner":("",""), # a tuple of 2 strings
    
    "name":"", # a string

    "description":"", # a string
    
    "author(s)":[], # a set of tuples of 2 strings

    "identifier":"", # a string -> generated during model curation !

    "code_location": "", # a string

    "public":"", # a string either "TRUE" or "FALSE" (the inverse of private in the Model Catalog)
    
    # ------ KG METADATA -------- # 
    "abstraction_level":("",""), # a tuple of 2 strings
    "brain_region":("",""), # a tuple of 2 strings
    "cell_type":[], # a set of strings
    "creation_date":"", # a string
    "model_scope":("",""), # a tuple of 2 strings
    "model_type":("",""), # a tuple of 2 strings
    "organization":("",""), # a tuple of 2 strings
    "pla_components":("",""), # a tuple of 2 strings
    "project":("",""), # a tuple of 2 strings
    "associated_dataset":[], # a set of tuples of 2 strings
    "associated_method":[], # a set of tuples of 2 strings
    "associated_experimental_preparation":[], # a set of tuples of 2 strings
    "used_software":[], # a set of tuples of 2 strings
    "code_format": ("",""), # a tuple of 2 strings
    "license": ("",""), # a tuple of 2 strings
    "parameters": "", # a string
    
    # ------ IMAGES -------- # 
     "images":[], # list of dictionaries
    # elements of the "images" list should be of the form:
    # {"url":"",
    #  "caption":""}
}
```

## Configuration file

A file 

```
import os
# KEYS_FOR_MODEL_ENTRIES = [ # in the order you wish it to appear on the sheet !!
#     "alias", "owner", "name", "description", "author(s)", "identifier", 
#     "versions", "code_location", "private",
#     "abstraction_level", "brain_region", "cell_type",
#     "creation_date", "license", "model_scope", "model_type",
#     "organization", "pla_components", "project",
#     "associated_dataset", "associated_method",
#     "associated_experimental_preparation", "used_software",
#     "code_format", "license", "parameters", "images"
#

```

Same thing for the keys visibles in the /KG Release Summary/ sheet, it is now set by (in =src/spreadsheet_db.py=):

```
KEYS_FOR_RELEASE_SUMMARY = [s+' ?' for s in list(template.keys())[:2]]
KEYS_FOR_RELEASE_SUMMARY += ['Total Score', 'Score for Release', 'Released ?']
```

you can manually construct the list for the fields that you want to visualize. Of course, you will have to adapt the shape/visualization of the spreadsheet afterwards.

```

## Stats

A detailed analysis of the curation pipeline is available at:

https://github.com/yzerlaut/model-curation/blob/master/stats/summary.org

