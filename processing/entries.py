
def concatenate_words(words, istring=100, istringmin=2):
    alias = ''
    for word in words:
        if len(word)>=istringmin:
            alias += word[:istring].capitalize()
    return alias
    
def version_naming(name):

    return name.replace('et al.', '').replace(',', '.').replace(' ', '')
    
    
def find_meaningfull_alias(name,
                           istringmax=30):
    """
    we try to limit the alias to ~40 characters
    """
    name = name.replace(',', '') # a bit of preprocessing
    
    if len(name.split(' '))==1: # this means it is not real text, that's a real alias
        return name
    else:
        words = name.split(' ')
        
        istring, alias = 20, concatenate_words(words, istring=20)
        while (len(alias)>istringmax) and (istring>1):
            istring -=1
            alias = concatenate_words(words, istring=istring)
            

        return alias[:istringmax]

def reformat_from_catalog(key, template_value, catalog_value):

    if key=='author(s)':
        # dealing with , and &
        author_list0 = catalog_value.split(',')
        author_list=[]
        for author in author_list0:
            if len(author.split('&'))>1:
                author_list += author.split('&')
            elif len(author.split(' and '))>1:
                author_list += author.split(' and ')
            else:
                author_list.append(author)
        return [(author,"") for author in author_list]
    elif key=='public':
        return str(not bool(catalog_value))
    elif (key=='creation_date') or (key=='timestamp'):
        return catalog_value[:19] # limiting time info to the second 
    elif type(template_value) is tuple:
        return (catalog_value, "")
    else:
        return catalog_value


def reformat_for_spreadsheet(key, val):
    if type(val) is list:
        output = ''
        for elem in val:
            if type(elem) is tuple:
                output += str(elem[0])
            elif type(elem) is dict:
                output += elem['family_name']+', '+elem['given_name']
            else:
                output += str(elem)
            output += ', '
        return output[:-2]
    elif type(val) is tuple:
        return str(val[0])
    elif type(val) is dict:
        return val['family_name']+', '+val['given_name']
    elif key=='images':
        return str(len(val)) # just the number of images
    else:
        return str(val)
    
def reformat_date_to_timestamp(tmstmp):
    """
    transforms the datetime string into a number (to allow easy sorting by date)
    """
    return str(tmstmp[:19]).replace(':','').replace(' ','').replace('-','')
