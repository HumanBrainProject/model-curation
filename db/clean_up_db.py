import os, sys, pathlib
import numpy as np

backup_files = []
for fn in os.listdir(os.path.join(pathlib.Path(__file__).resolve().parent, 'backups')):
    if len(fn.split('-'))==2:
        backup_files.append(fn)


def convert_to_int(filename):
    date, time = filename.split('-')
    time = time.replace('.pkl', '')
    Y, M, D = date.split('.')
    h, m, s = time.split(':')
    factor = [1., 60., 60., 24., 30., 12.]
    for i in range(len(factor)-1):
        factor[i+1] = factor[i+1]*factor[i]

    dt = np.array([float(t) for t in [s, m, h, D, M, Y]])
    return np.sum(factor*dt)

backup_files_dates = np.array([convert_to_int(f) for f in backup_files])


try:
    N = int(sys.argv[-1])
except ValueError:
    N = 20

isorted = np.argsort(backup_files_dates)[::-1]

to_be_kept = np.concatenate([[0], np.random.choice(np.arange(1, len(isorted)), N-1, replace=False)])
print(to_be_kept)
for i in range(len(isorted)):
    if i not in to_be_kept:
        os.remove(os.path.join('db', 'backups', backup_files[isorted[i]]))
    else:
        print(backup_files[isorted[i]], 'kept')

