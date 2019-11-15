import requests, sys, os

def get_email(first_name, last_name, token):

    url = 'https://services.humanbrainproject.eu/idm/v1/api/user/search?displayName=*'+first_name+' '+last_name+'*'
    headers={"authorization":"Bearer "+ token }

    res = requests.get(url, headers=headers)
    
    email = ""
    if not res.status_code != 200:
        res = res.json()['_embedded']['users']
        if len(res) >0:
            res = res[0]
            email = res['emails'][0]['value']
            print('email found: %s' % email)
    if email == "":
        email = input('email not found for: %s %s , please enter it manually:\n' % (first_name, last_name))
        
    return email


if __name__ == '__main__':

    if len(sys.argv)==3:
        print(get_email(sys.argv[1], sys.argv[2], os.environ["HBP_token"]))
    else:
        print('execute as "python emails.py FirstName Lastname" ')

