import seaborn as sns
import matplotlib.pyplot as plt
import os
from scipy.sparse import csr_matrix
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, 'codes/gmapy')
from gmapi.mappings.compound_map import CompoundMap
from gmapi.mappings.priortools import propagate_mesh_css
from gmapi.inference import compute_posterior_covmat


def save_result(res, is_std2017=False,
                fix_sacs_jacobian=True, legacy_integration=False,
                rel_to_std2017=True):

    if is_std2017:
        os.makedirs('eval2017', exist_ok=True)
    else:
        os.makedirs('results', exist_ok=True)

    tbl = res['table']
    # produce the tables with the Pu9/U5(n,f) ratios, and SACS and SACS ratios
    ens_u5 = list(tbl.loc[tbl.NODE.str.fullmatch('xsid_8'), 'ENERGY'])
    ens_pu9 = list(tbl.loc[tbl.NODE.str.fullmatch('xsid_9'), 'ENERGY'])
    ens_u8 = list(tbl.loc[tbl.NODE.str.fullmatch('xsid_10'), 'ENERGY'])
    common_ens_u5_pu9 = np.sort(list(set(ens_u5).intersection(ens_pu9)))
    common_ens_u5_u8 = np.sort(list(set(ens_u5).intersection(ens_u8)))

    testdf_list = []
    testdf_list.append(pd.DataFrame({
        'NODE': 'exp_ratio_pu9_u5',
        'ENERGY': common_ens_u5_pu9,
        'REAC': 'MT:3-R1:9-R2:8',
        }))
    testdf_list.append(pd.DataFrame({
        'NODE': 'exp_ratio_u8_u5',
        'ENERGY': common_ens_u5_u8,
        'REAC': 'MT:3-R1:10-R2:8',
        }))
    # without U8 SACS because legacy integration fails for U8 SACS
    testdf_list.append(pd.DataFrame({
        'NODE': ['exp_sacs_' + r for r in [
            'u5', 'pu9', 'pu9/u5', 'u5/pu9',
            ]],
        'ENERGY': 0.,
        'REAC': ['MT:6-R1:8', 'MT:6-R1:9', 'MT:10-R1:9-R2:8', 'MT:10-R1:8-R2:9']
        }))
    # we also create the dataframe skeleton with U8 SACS
    # and ratios included for meaningful comparisons
    # with later numerical experiments
    sacs_related_u8_df = pd.DataFrame({
        'NODE': ['exp_sacs_' + r for r in [
            'u8', 'u8/u5', 'pu9/u8'
            ]],
        'ENERGY': 0.,
        'REAC': ['MT:6-R1:10', 'MT:10-R1:10-R2:8', 'MT:10-R1:9-R2:10']
        })
    if not legacy_integration:
        testdf_list.append(sacs_related_u8_df)
    testdf = pd.concat(testdf_list, axis=0, ignore_index=True)

    source_idcs = res['idcs']
    target_idcs = np.arange(len(tbl), len(tbl)+len(testdf))
    exttbl = pd.concat([tbl, testdf], axis=0, ignore_index=True)
    # xs obtained according to Fortran GMAP with bugs present
    # but in the forward propagation we do it correctly.
    # NOTE: legacy_integration from False to True
    #       leads to 0.23% increase in Pu9(n,f) SACS (1.805 to 1.8007)
    compmap = CompoundMap(fix_sacs_jacobian=True, legacy_integration=legacy_integration)
    fullpostvals = exttbl.PRIOR.to_numpy()
    fullpostvals[source_idcs] = exttbl.loc[source_idcs, 'POST'].to_numpy()
    propvals = propagate_mesh_css(exttbl, compmap, fullpostvals, prop_normfact=False)
    postvals = propvals[source_idcs]
    if is_std2017:
        if not np.allclose(propvals[:len(tbl)], exttbl.POST[:len(tbl)].to_numpy()):
            raise ValueError('Do you really recompute the standards 2017, dude?')
    exttbl.POST = propvals
    # the legacy run_gmap function returns the covariance matrix
    # and not its inverse, so we have to invert it.
    # In general, for nuclear data problems it is beneficial
    # to work with the inverse posterior covariance matrix.
    invpostcov = csr_matrix(np.linalg.inv(res['postcov']))
    propcov = compute_posterior_covmat(compmap, exttbl, postvals, invpostcov,
                                       source_idcs=source_idcs, idcs=target_idcs)

    # relative uncertainties are just soooo much more pleasant to look at
    exttbl.loc[target_idcs, 'POSTUNC'] = np.sqrt(propcov.diagonal())
    exttbl.loc[target_idcs, 'RELPOSTUNC'] = (
            exttbl.loc[target_idcs, 'POSTUNC'] / exttbl.loc[target_idcs, 'POST']
        )

    # save the results as csv files
    ratio_df = exttbl[exttbl.NODE.str.match('(exp_ratio_|xsid_)')]
    for _, curdf in ratio_df.groupby('NODE'):
        curreac = str(curdf.REAC.iloc[0]).replace(':', '-')
        curdf = curdf.drop(curdf.columns.difference([
            'ENERGY', 'POST', 'POSTUNC', 'RELPOSTUNC'
            ]), axis=1, inplace=False).reset_index(drop=True)

        if rel_to_std2017:
            stdfile = 'result_' + curreac + '.csv'
            curdf2017 = pd.read_csv(os.path.join('eval2017', stdfile),
                                    header=0, index_col=False)
            curdf.POST = curdf.POST / curdf2017.POST - 1
            resfile = 'result_' + curreac + '_relto_std2017.csv'
        else:
            resfile = 'result_' + curreac + '.csv'

        if is_std2017:
            respath = os.path.join('eval2017', resfile)
        else:
            respath = os.path.join('results', resfile)

        curdf.to_csv(respath, header=True, index=False)

    # we aggregate all SACS and SACS ratios in one file
    sacs_df = exttbl[exttbl.NODE.str.match('exp_sacs_')]
    if not legacy_integration:
        sacs_df = pd.concat([sacs_df, sacs_related_u8_df], axis=0, ignore_index=True)
    sacs_df = sacs_df.drop(sacs_df.columns.difference([
        'NODE', 'REAC', 'POST', 'POSTUNC', 'RELPOSTUNC'
        ]), axis=1)
    resfile = 'result_sacs.csv'

    if is_std2017:
        respath = os.path.join('eval2017', resfile)
    else:
        respath = os.path.join('results', resfile)

    sacs_df.NODE = sacs_df.NODE.str.replace('exp_', '')
    #  sacs_df.columns = sacs_df.columns.str.replace('NODE', 'REAC')
    sacs_df.to_csv(respath, header=True, index=False)

    # some correlation matrix of the SACS reactions
    # NOTE: neither testdf nor exttbl contain U8 SACS or related ratios
    sacs_idcs = testdf.index[testdf.NODE.str.match('exp_sacs_')]
    sacs_uncs = exttbl.loc[exttbl.NODE.str.match('exp_sacs'), 'POSTUNC'].to_numpy()
    sacs_covmat = propcov[np.ix_(sacs_idcs, sacs_idcs)].toarray()
    sacs_cormat = sacs_covmat / sacs_uncs.reshape(-1, 1) / sacs_uncs.reshape(1, -1)
    red_sacs_df = testdf.loc[sacs_idcs]

    sns.set(rc = {'figure.figsize': (7,7)})
    ax = sns.heatmap( sacs_cormat, annot=True,
                     xticklabels=red_sacs_df['NODE'].str.replace('exp_sacs_',''),
                     yticklabels=red_sacs_df['NODE'].str.replace('exp_sacs_',''))
    if is_std2017:
        ax.set_title('Correlations between SACS and SACS ratios (std2017)')
    else:
        ax.set_title('Correlations between SACS and SACS ratios')
    resfile = 'result_sacs_corplot.png'
    if is_std2017:
        respath = os.path.join('eval2017', resfile)
    else:
        respath = os.path.join('results', resfile)
    ax.figure.savefig(respath)
