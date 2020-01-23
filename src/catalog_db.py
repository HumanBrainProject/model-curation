import sys, os, pathlib
import numpy as np
import pickle, pprint
import time

from fairgraph.client import KGClient
from fairgraph.base import KGProxy
from fairgraph.brainsimulation import ModelProject, ModelInstance #, AbstractionLevel, BrainStructure, CellularTarget, License, ModelFormat, ModelScope, Publication, StudyTarget, FileBundle


def load_models(client):
    
    models = ModelProject.list(client)
    
    return models

def load_model_instances(client):

    MODEL_INSTANCES = []

    models = ModelProject.list(client, size=1000)
    for model in models:
        # print('----------------------------------------')
        # print('- %s ' % model.name)
        if type(model.instances) is list:
            for modelI in model.instances:
                MODEL_INSTANCES.append(modelI.resolve(client))
        elif type(model.instances) is KGProxy:
            minst_proxy = model.instances
            MODEL_INSTANCES.append(minst_proxy.resolve(client))
        else:
            print('Ignoring %s @ %s' % (model.name, model.date_created))
            pass # we don't care about models without specific version
        
    DATES = np.array([time.mktime(minst.timestamp.timetuple()) for minst in MODEL_INSTANCES])

    
    return [MODEL_INSTANCES[i] for i in np.argsort(DATES)]


if __name__=='__main__':
    
    client = KGClient(os.environ["HBP_token"])
    # models = load_models(client)

    MODEL_INSTANCES = load_model_instances(client)
    for i, minst in enumerate(MODEL_INSTANCES):
        print(i, ') ', minst.name)
