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

    "private":"", # a string either "TRUE" or "FALSE"
    
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
