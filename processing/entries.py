

def refactor_model_entries(models):

    for model in models:
        for key, val in model.items():
            if len(val.split('None'))>1:
                model[key] = 'None'
                
    return models
    
