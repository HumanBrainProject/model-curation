import sys, os, pathlib
from datetime import datetime
import numpy as np
import pickle, time, pprint
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

def create_a_backup_version(models):
    """
    create a backup pkl datafile in the "local_db_backups" directory
    """
    pkl_file = open(os.path.join(str(pathlib.Path(__file__).resolve().parents[1]),
                                 'db', 'backups',
                                 datetime.now().strftime("%Y.%m.%d-%H:%M:%S.pkl")), 'wb')
    pickle.dump(models, pkl_file)
    pkl_file.close()


def save_models(models):
    """ """
    pkl_file = open(os.path.join(pathlib.Path(__file__).resolve().parents[1],
                                 'db', 'LocalDB.pkl'), 'wb')
    pickle.dump(models, pkl_file)
    pkl_file.close()

def load_models(filename=None):
    """ """
    if filename is None:
        filename = os.path.join(pathlib.Path(__file__).resolve().parents[1],
                                'db', 'LocalDB.pkl')
    pkl_file = open(filename, 'rb')
    models = pickle.load(pkl_file)
    pkl_file.close()
    
    # we sort them by creation date (the last one is the newest)
    dates = np.array([time.mktime(minst['date_created'].timetuple()) for minst in models])
    return [models[i] for i in np.argsort(dates)[::-1]]

def show_list():
    
    models = load_models()

    for i, minst in zip(range(len(models))[::-1], models[::-1]):
        if (len(minst['name'].split('IGNORE'))==1) and (minst['name'] not in ['skjdfhskjdfh @ sadf', 'lkfjgldkfgj @ sfdgdfg', 'lkfjgldkfgj @']) and (len(minst['name'].split('MEModel'))==1 or show_ME):
            print(i+1, ') ', minst['name'].replace('ModelInstance for ', ''))
            

def get_model_attributes():
    models = load_models()
    return models[0].keys()


def update_entry_manually(models, index, args):

    if (args.key in models[index]) and (args.value is not None):
        if type(models[index][args.key]) is str:
            if input('Do you want to replace the value "%s" for key "%s" by: "%s" ? y/[n]\n' % (models[index][args.key], args.key, args.value[0])) in ['y', 'yes']:
                models[index][args.key] = args.value[0]
                print('[ok] value changed to', models[index][args.key])
            else:
                print('[!!] value not changed')
        elif type(models[index][args.key]) is tuple:
            if input('Do you want to replace the value "%s" for key "%s" by: "%s" ? y/[n]\n' % (models[index][args.key][0], args.key, args.value[0])) in ['y', 'yes']:
                models[index][args.key] = (args.value[0], '')
                print('[ok] value changed to', models[index][args.key])
            else:
                print('[!!] value not changed')
        elif type(models[index][args.key]) is list:
            if input('Do you want to replace the value "%s" for key "%s" by: "%s" ? y/[n]\n' % (models[index][args.key], args.key, args.value)) in ['y', 'yes']:
                models[index][args.key] = []
                print(args.value)
                for elem in args.value:
                    models[index][args.key].append((elem, ''))
                print('[ok] value changed to', models[index][args.key])
            else:
                print('[!!] value not changed')
    elif (args.key in models[index]):
        print('The value for key %s is currently: %s' % (args.key, models[index][args.key]))
    else:
        pprint.pprint(models[index])
        print('[!!] key not found')


if __name__=='__main__':
    create_a_backup_version(load_models())
    models = load_models()
    save_models(models)
    # print(models[4].keys())
    # print(models[4]['author'])
                            
