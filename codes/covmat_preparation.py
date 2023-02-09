# run from the root of the repository 
import os
import pickle
import pandas as pd
import numpy as np

os.chdir('results')

with open('evaluation.pkl', 'rb') as f:
    res = pickle.load(f)

df = res['table']
# extract adjusted quantities (cross sections and normalization) and get rid of experimental data points
resdf = df.loc[res['idcs']].reset_index()
postcov = res['postcov']

# extract Pu9 rows of dataframe
pu9df = resdf[resdf.REAC == 'MT:1-R1:9']
print(pu9df)
pu9_idcs = np.array(pu9df.index)
pu9_cov = postcov[np.ix_(pu9_idcs, pu9_idcs)]

# construct relative covariance matrix from absolute one
rel_pu9_cov = pu9_cov / pu9df.POST.values.reshape(1, -1) / pu9df.POST.values.reshape(-1, 1)

# for checking: print minimum relative and maximum relative uncertainty (min: 0.003 = 0.3% max: 0.047 = 4%)
print(np.min(np.sqrt(np.diag(rel_pu9_cov))))
print(np.max(np.sqrt(np.diag(rel_pu9_cov))))

# add 1.2% USU component
usu_comp = np.full(len(pu9df), 0.012)
usu_cov = usu_comp.reshape(1,-1) * usu_comp.reshape(-1, 1)

final_rel_pu9_cov = rel_pu9_cov + usu_cov

# quick check: eigenvalues
eigstruc = np.linalg.eig(final_rel_pu9_cov)
print(np.min(eigstruc[0]))

# save the matrix
np.savetxt('pu9cov.csv', final_rel_pu9_cov, delimiter=',')

# also save energies to csv
energies = pu9df.ENERGY.values
np.savetxt('pu9_energies.csv', energies, delimiter=',')
