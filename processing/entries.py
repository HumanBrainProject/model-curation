

def reformat_from_catalog(key, template_value, catalog_value):

    if key=='author(s)':
        return [(author,"") for author in catalog_value.split(',')]
    elif (key=='creation_date') or (key=='timestamp'):
        return catalog_value[:19] # limiting time info to the second 
    elif type(template_value) is tuple:
        return (catalog_value, "")
    else:
        return catalog_value

def reformat_date_to_timestamp(tmstmp):
    """
    transforms the datetime string into a number (to allow easy sorting by date)
    """
    return str(tmstmp[:19]).replace(':','').replace(' ','').replace('-','')

    
