from endf_parserpy.endf_parser import BasicEndfParser
import numpy as np
import os


def apply(prior_list):
    parser = BasicEndfParser()
    endf_file = os.path.join('auxiliary_data', 'IRDFF-II_Cf252_spectrum.endf')
    cf252_endf = parser.parsefile(endf_file)
    # get fission spectrum
    mf3 = cf252_endf[3][261]
    en = np.array(mf3['xstable']['E']) / 1e6
    xs = np.array(mf3['xstable']['xs']) * 1e6
    # get data to reconstruct covariance matrix
    mf33 = cf252_endf[33][261]
    E = mf33['subsection'][1]['ni_subsection'][1]['E']
    F = mf33['subsection'][1]['ni_subsection'][1]['F']
    # reconstruct covariance matrix
    energies = np.array(tuple(E.values())) / 1e6
    n = len(energies)-1
    covmat = np.ones((n, n), dtype='d') * 0.01**2 + np.identity(n) * 0.01

    fis_idx = None
    for idx, curprior in enumerate(prior_list):
        if curprior['type'] == 'legacy-fission-spectrum':
            fis_idx = idx
            break
    assert fis_idx is not None
    prior_list.pop(fis_idx)

    # add the IRDFF-II Cf-252 spectrum in a
    # new prior blocktype (experimental extension)
    new_fis_block = {
        'type': 'modern-fission-spectrum',
        'energies': en.tolist(),
        'spectrum': xs.tolist(),
        'covmat':  {
            'energies': energies.tolist(),
            'matrix': covmat.tolist()
        }
    }
    prior_list.append(new_fis_block)
    return prior_list
