import os
from fairgraph.client import KGClient
from fairgraph.uniminds import Person, ModelInstance, Dataset


def KG_db(n=100000):

    client = KGClient(os.environ["HBP_token"])
    models = ModelInstance.list(client, api="query", resolved=True, size=3)

    return models[0].__attributes__

    for i, m in enumerate(models):
        print("- %i) %s" %(i, m.name))


minst = ModelInstance(name="Test by yann"
                      description='this is a test description',
                      brain_region='brain',
                      species='Homo Sapiens',
                      model_of=None,
                      version='v1')
minst.save(client)
# def get_list_of_models(n=100):

#     List = {'name':[], 'custodian':[]}
#     for model in ModelInstance.list(client, size=n):
#         List['custodian'].append(str(model.custodian))
#         List['name'].append(model.name)
#     return List

# if __name__ == '__main__':

#     print(get_list_of_models(n=10))
#     print(ModelInstance.list(client))
