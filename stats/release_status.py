import numpy as np
import matplotlib.pylab as plt
import datetime

import os, sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from mc_src import local_db

models = local_db.load_models()

model_names = np.array([m['name'] for m in models], dtype=str) # model names in LocalDB
released_in_KG = np.array([m['released_in_KG'] for m in models], dtype=str)

keys = ['brain_region', 'abstraction_level', 'model_scope', 'organization']
AL_entries = ['cognitive modelling',
              'population modelling',
              'spiking neurons',
              'systems biology']
BR_entries =  ['basal ganglia',
               'cerebellum',
               'cerebral cortex',
               'hippocampus',
               'primary auditory cortex',
               'somatosensory cortex',
               'striatum',
               'whole brain']
MS_entries = ['network',
              'network: brain region',
              'network: microcircuit',
              'network: whole brain',
              'single cell',
              'subcellular',
              'subcellular: signalling']
O_entries = ['Blue Brain Project',
             'HBP-SP1',
             'HBP-SP3',
             'HBP-SP4',
             'HBP-SP5',
             'HBP-SP6',
             'HBP-SP9',
             'KOKI-UNIC',
             'KTH-UNIC']

fig, AX = plt.subplots(2, len(keys), figsize=(3.5*len(keys),5))
plt.subplots_adjust(left=.03, right=.9, top=.88, bottom=.1, wspace=.6, hspace=.9)

plt.annotate('* %s *' % str(datetime.date.today()),
             (.01, .97), xycoords='figure fraction', style='italic', size=12,
             ha='left', va='center')

plt.annotate('Model Catalog: %i entries' % len(np.unique(model_names)),
             (.5, .97), xycoords='figure fraction', weight='bold', size=12,
             ha='center', va='center')

N_in_KG = np.sum([1 if m['released_in_KG']=='True' else 0 for m in models])
plt.annotate('EBrains Knowledge Graph: %i entries' % N_in_KG,
             (.5, .47), xycoords='figure fraction', weight='bold', size=12,
             ha='center', va='center')

for i, key in enumerate(keys):
    new_key = "".join([k.capitalize()+' ' for k in key.split('_')])
    AX[0,i].set_title(new_key, style='italic')
    AX[1,i].set_title(new_key, style='italic')

# looping over keys
for kk, key, entries in zip(range(len(keys)), keys,
                            [BR_entries, AL_entries, MS_entries,O_entries]):

    entries_count = np.zeros(len(entries)+1)
    entries_count_KG = np.zeros(len(entries)+1)
    for name in np.unique(model_names):
        # Model Catalog
        i0 = np.argwhere(name==model_names).flatten()[0]
        counted = False
        for ik, k in enumerate(entries):
            if models[i0][key][0]==k:
                counted=True
                entries_count[ik] +=1
        for ik, k in enumerate(entries):
            if not counted and len(models[i0][key][0].split(k))>1:
                counted=True
                entries_count[ik] +=1
        if not counted:
            entries_count[-1] +=1
        # Knowledge Graph
        i0 = np.argwhere((name==model_names) & (released_in_KG=='True')).flatten()
        if len(i0)>0:
            i0, counted = i0[0], False
            for ik, k in enumerate(entries):
                if models[i0][key][0]==k:
                    counted=True
                    entries_count_KG[ik] +=1
            for ik, k in enumerate(entries):
                if not counted and len(models[i0][key][0].split(k))>1:
                    counted=True
                    entries_count_KG[ik] +=1
            if not counted:
                entries_count_KG[-1] +=1

    
    final_entries = entries_count[:-1]
    AX[0,kk].pie(final_entries, labels=entries,
                 autopct=lambda p:'{:.0f}'.format(p * np.sum(final_entries) / 100))
    AX[0,kk].annotate('other: %i (%.0f%%)' % (entries_count[-1],
                                       100.*entries_count[-1]/np.sum(entries_count)),
                                              (0.5,0.),
                      xycoords='axes fraction', ha='center', va='top')
    final_entries = entries_count_KG[:-1]
    AX[1,kk].pie(final_entries, labels=entries,
                 autopct=lambda p:'{:.0f}'.format(p * np.sum(final_entries) / 100))
    AX[1,kk].annotate('other: %i (%.0f%%)' % (entries_count_KG[-1],
                                  100.*entries_count_KG[-1]/np.sum(entries_count_KG)),
                                              (0.5,0.),
                      xycoords='axes fraction', ha='center', va='top')
    # # looping over models

plt.savefig(os.path.join(str(pathlib.Path(__file__).resolve().parents[0]), 'figs', 'release_status.png'))
