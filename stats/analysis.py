import os, sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pylab as plt
import datetime

from src import local_db

models = local_db.load_models()


# dict_keys(['alias', 'owner', 'name', 'description', 'author(s)', 'version', 'identifier', 'code_location', 'license', 'public', 'abstraction_level', 'brain_region', 'cell_type', 'creation_date', 'model_scope', 'organization', 'associated_dataset', 'pla_components', 'project', 'associated_method', 'associated_experimental_preparation', 'used_software', 'code_format', 'model_type', 'parameters', 'images', 'in_KG', 'released_in_KG', 'KG_identifier', 'KG_id', 'timestamp'])


if sys.argv[-1]=='author':

    model_authors = np.array([m['author(s)'][0] for m in models], dtype=str)

    
    fig, AX = plt.subplots(1, 2, figsize=(3.5*2,3))
    plt.annotate('Number of contributing authors: %i' % len(np.unique(model_authors)),
                 (.5, .97), xycoords='figure fraction', weight='bold', size=12,
                 ha='center', va='center')
    plt.subplots_adjust(left=.2, right=.9, top=.75, bottom=.1, wspace=.6, hspace=.9)

    AX[0].set_title('# of models / author')
    AX[1].set_title('# of authors / model')

    plt.show()
    
elif sys.argv[-1]=='custodian':

    model_custodian = np.array([m['owner'] for m in models], dtype=str)

    print(len(np.unique(model_custodian)))
    # mg.hist()
    
