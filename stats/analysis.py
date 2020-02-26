import os, sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pylab as plt
import datetime

from mc_src import local_db

models = local_db.load_models()


# dict_keys(['alias', 'owner', 'name', 'description', 'author(s)', 'version', 'identifier', 'code_location', 'license', 'public', 'abstraction_level', 'brain_region', 'cell_type', 'creation_date', 'model_scope', 'organization', 'associated_dataset', 'pla_components', 'project', 'associated_method', 'associated_experimental_preparation', 'used_software', 'code_format', 'model_type', 'parameters', 'images', 'in_KG', 'released_in_KG', 'KG_identifier', 'KG_id', 'timestamp'])

if sys.argv[-1]=='version':
    print(len(np.unique([m['name'] for m in models])), 'models')

    
elif sys.argv[-1]=='author':

    model_authors = np.empty(0, dtype=str)
    for m in models:
        model_authors = np.concatenate([model_authors, [mm[0] for mm in m['author(s)']]])
    model_per_author = np.zeros(len(models))
    for auth in np.unique(model_authors):
        model_per_author[int(np.sum(model_authors==auth))]+=1
    
    fig, AX = plt.subplots(1, 2, figsize=(3.5*2,3))
    plt.annotate('Number of contributing authors: %i' %\
                 len(np.unique(model_authors)),
                 (.5, .95), xycoords='figure fraction', weight='bold', size=12,
                 ha='center', va='center')
    plt.subplots_adjust(left=.2, right=.9, top=.8, bottom=.25, wspace=.6, hspace=.9)
    AX[0].set_title('number of models per author')
    AX[0].bar(np.arange(len(model_per_author[model_per_author>0]))+1,
              model_per_author[model_per_author>0])
    AX[0].set_yticks([1,10,100], ['1', '10', '100'])
    AX[0].set_yticklabels(['1', '10', '100'])
    AX[0].set_yscale('log')
    AX[0].set_ylabel('author count')
    AX[0].set_xlabel('# of models')
    
    AX[1].set_title('number of authors per model')

    plt.show()
    
elif sys.argv[-1]=='custodian':

    model_custodian = np.array([m['owner'] for m in models], dtype=str)

    print(len(np.unique(model_custodian)))
    # mg.hist()
    
