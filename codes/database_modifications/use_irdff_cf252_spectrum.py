from endf_parserpy.endf_parser import BasicEndfParser
import numpy as np
import os


def apply(prior_list):
    parser = BasicEndfParser()
    endf_file = os.path.join('auxiliary_data', 'IRDFF-II_Cf252_spectrum.endf')
    cf252_endf = parser.parsefile(endf_file)
    # get fission spectrum
    mf3 = cf252_endf[3][261]
    en = mf3['xstable']['E']
    xs = mf3['xstable']['xs']
    # get data to reconstruct covariance matrix
    mf33 = cf252_endf[33][261]
    E = mf33['subsection'][1]['ni_subsection'][1]['E']
    F = mf33['subsection'][1]['ni_subsection'][1]['F']
    # reconstruct covariance matrix
    energies = tuple(E.values())
    n = len(energies)-1
    covmat = np.full((n, n), 0.0)
    for i in F.keys():
        for j in F[i].keys():
            covmat[i-1, j-1] = F[i][j]
            if i != j:
                covmat[j-1, i-1] = F[i][j]

    assert np.all(np.sort(energies) == energies)
    assert np.all(np.sort(en) == en)
    # remove the legacy fission spectrum
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
        'energies': en,
        'spectrum': xs,
        'covmat':  {
            'energies': energies,
            'i': i_list,
            'j': j_list,
            'x': v_list
        }
    }
    prior_list.append(new_fis_block)
    return prior_list
