

def refactor_model_entries(models):

    for model in models:
        for key, val in model.items():
            if type(val)==str and len(val.split('None'))>1:
                model[key] = 'None'
            if key=='creation_date':
                model[key] = val[:10].replace('-','')
                
    return models
    
