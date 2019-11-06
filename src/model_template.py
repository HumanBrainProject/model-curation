template = {
    
    "alias":"", # a string
    
    "version":"", # a string
    
    "owner":"", # a string
    
    "name":"", # a string

    "description":"", # a string
    
    "author(s)":[], # a set of a strings

    "identifier":"", # a string -> generated during model curation !

    "code_location": "", # a string

    "private":"", # a string either "TRUE" or "FALSE"
    
    # ------ KG METADATA -------- # 
    "abstraction_level":"", # a string
    "brain_region":"", # a string
    "cell_type":[], # a set of strings
    "creation_date":"", # a string
    "license":"", # a string
    "model_scope":"", # a string
    "model_type":"", # a string
    "organization":"", # a string
    "pla_components":"", # a string
    "project":"", # a string
    "associated_dataset":[], # a string
    "associated_method":[], # a string
    "associated_experimental_preparation":[], # a set of strings
    "used_software":[], # a set of strings
    "code_format": "", # a string
    "license": "", # a string
    "parameters": "", # a string
    
    # ------ VERSIONS -------- # 
    "images":[
	{"url":"",
	 "caption":""}
    ],
}
