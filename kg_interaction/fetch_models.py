import os
import numpy as np

from fairgraph.client import KGClient
from fairgraph.uniminds import Person, ModelInstance, Dataset

token = os.environ["HBP_token"]
#nexus_endpoint = "https://nexus-int.humanbrainproject.org/v0"
nexus_endpoint = "https://nexus.humanbrainproject.org/v0"
client = KGClient(token, nexus_endpoint=nexus_endpoint)


def get_list_of_models(n=100):

    List = {'name':[], 'custodian':[]}
    for model in Dataset.list(client, size=n):
        List['custodian'].append(str(model.custodian))
        List['name'].append(model.name)
    return List
print(get_list_of_models(10))
