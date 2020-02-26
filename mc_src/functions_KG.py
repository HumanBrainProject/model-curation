import os, sys, pathlib, requests

from fairgraph.client import KGClient
from fairgraph.uniminds import Person, ModelInstance, Dataset

def save_person_in_KG(client, first_name, last_name, email):
    person = Person(family_name=last_name,
                    given_name =first_name,
                    email=email,
                    affiliation='')
    if not person.exists(client):
        person.save(client)
        print('saved in KG: %s', person)
    else:
        print('already exists in KG: %s', person)

def get_email_from_collab(first_name, last_name,
                          token=os.environ['HBP_token']):
    
    url = 'https://services.humanbrainproject.eu/idm/v1/api/user/search?displayName=*'+\
          first_name+' '+last_name+'*'
    headers={"authorization":"Bearer "+ token }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print('cannot find the email from collab')
        ##email = raw_input('please enter e-mail by hand')
        email = "unknown@example.com"
    else:
        res = res.json()['_embedded']['users']
        print('user list found is:')
        for u in res:
            print(u)
        if len(res) >0:
            res = res[0]
            print('email found is: ',res['emails'][0]['value'])
            check = input('is this ok? [n]/y   ')
            if check in ('y', 'Y', 'yes'):
                email = res['emails'][0]['value']
            else:
                email = input('then, please enter e-mail by hand \n')
        else:
                ###email = raw_input('then, please enter e-mail by hand')
                email = "unknown@example.com"
                
    return email


def find_author_in_KG(author,
                      Person_list=None):
    """
    using the scope='released' filter to fetch released entries in the KG
    """
    print('Finding Persons in KG [...]')
    if Person_list is None:
        Person_list = Person.list(client, api='query',
                                  scope='inferred',
                                  size=100000)

    for person in Person_list:
        if (person.family_name is not None) and :
        # if str(person.given_name)+' '+str(person.family_name)==author:
            print(person.name)

        
        

if __name__ == '__main__':


    # sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
    # # from processing.entries import refactor_model_entries
    # from processing.names import resolve_name
    # from src import local_db

    client = KGClient(os.environ["HBP_token"])
    
    Person_list = Person.list(client, api='query',
                              scope='inferred', resolved=True,
                              size=100000)
    
    # email=get_email_from_collab('Yann', 'Zerlaut')
    # print(email)
    # save_person_in_KG(client, 'Yann', 'Zerlaut', email)
    # print(get_email_from_collab('Yann', 'Zerlaut'))
    # person = Person(family_name='Zerlaut',
    #                 given_name ='Yann',
    #                 email='yann.zerlaut@iit.it')
    # print(person.exists(client, api='query'))

    find_author_in_KG('Maurizio Mattia')
