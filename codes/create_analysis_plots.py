import os
import re
import pandas as pd
import numpy as np
from gmapi import GMADatabase
import matplotlib.pyplot as plt
from gmapi.mappings.compound_map import CompoundMap


plotdir = 'plots'
dbdir='database'
dbnames = [
    'data2017',
    'data2017_without_sacs',
    'data2017_with_mannhart_sacs',
    'data',
    'data_without_sacs',
    'data_with_mannhart_sacs'
    ]


os.makedirs(plotdir)

gmadbs = {
    nm: GMADatabase(os.path.join(dbdir, nm + '.json'))
        for nm in dbnames
    }

for k, gmadb in gmadbs.items():
    print('evaluating ' + k)
    gmadb.evaluate(correct_ppp=True)


linestyles = ['solid', 'dotted', 'dashed', 'dashdot', (5,(10,3)), (0,(5,11)), (0,(3,1,1,1,1))]

refdf = gmadbs['data2017'].get_datatable() 
newdfs = {k: db.get_datatable() for k, db in gmadbs.items()} 
refxsdf = refdf[refdf.NODE.str.match('xsid_')].copy()
for k, v in newdfs.items():
    new_post_colname = 'POST_' + k
    redv = v[v.NODE.str.match('xsid_')].copy()
    refxsdf[new_post_colname] = redv['POST'] / refxsdf['POST'] 

for k, v in newdfs.items():
    new_post_colname = 'POST_' + k
    new_postunc_colname = 'POSTUNC_' + k
    redv = v[v.NODE.str.match('xsid_')].copy()
    refxsdf[new_post_colname] = redv['POST'] / refxsdf['POST'] 
    refxsdf[new_postunc_colname] = redv['POSTUNC'] / redv['POST']


def pdf_metadata():
    return {
            'Creator': None,
            'Producer': None,
            'CreationDate': None
        }


def create_xs_to_ref_plots(energy_range, yrange, reacstrings):
    """Plots of Evaluated xs relative to evaluated std2017 xs."""
    for reacstr in reacstrings:
        reac_descr = refxsdf[refxsdf.REAC.str.match(reacstr)].DESCR.iloc[0]
        plot_cols = [c for c in refxsdf.columns if c.startswith('POST_data')]
        energy = refxsdf[refxsdf.REAC.str.match(reacstr)].ENERGY.to_numpy()
        for i, curcol in enumerate(plot_cols):
            curlabel = curcol.replace('POST_','').replace('data_', 'data_feb2022_')
            if curlabel == 'data':
                curlabel = 'data_feb2022'
            curxs = refxsdf[refxsdf.REAC.str.match(reacstr)][curcol].to_numpy()
            plt.plot(energy, curxs, label=curlabel, linestyle=linestyles[i])
        # set axis range
        plt.legend(loc='upper right', prop={'size': 6})
        plt.xlim(energy_range)
        plt.ylim(yrange)
        plt.xlabel('energy [MeV]')
        plt.ylabel('xs / xs2017')
        plt.title(reac_descr)
        # sanitize filename
        fname = 'ratio_plot_' + re.sub('[(),]', '_', reac_descr) + '_from_' + str(energy_range[0]) + '_to_' + str(energy_range[1]) + '.pdf'
        plt.savefig(os.path.join(plotdir, fname), dpi=150, bbox_inches='tight', metadata=pdf_metadata())
        plt.clf()


def create_uncertainty_plots(energy_range, yrange, reacstrings):
    """Plots of evaluated uncertainties."""
    for reacstr in reacstrings:
        reac_descr = refxsdf[refxsdf.REAC.str.match(reacstr)].DESCR.iloc[0]
        plot_cols = [c for c in refxsdf.columns if c.startswith('POSTUNC_data')]
        energy = refxsdf[refxsdf.REAC.str.match(reacstr)].ENERGY.to_numpy()
        for i, curcol in enumerate(plot_cols):
            curlabel = curcol.replace('POSTUNC_','').replace('data_', 'data_feb2022_')
            if curlabel == 'data':
                curlabel = 'data_feb2022'
            curunc = refxsdf[refxsdf.REAC.str.match(reacstr)][curcol].to_numpy()
            plt.plot(energy, curunc, label=curlabel, linestyle=linestyles[i])
        plt.legend(loc='upper right', prop={'size': 6})
        plt.xlim(energy_range)
        plt.ylim([0.004,0.01])
        plt.xlabel('energy [MeV]')
        plt.ylabel('relative uncertainty')
        plt.title(reac_descr)
        fname = 'uncertainty_plot_' + re.sub('[(),]', '_', reac_descr) + '_from_' + str(energy_range[0]) + '_to_' + str(energy_range[1]) + '.pdf'
        plt.savefig(os.path.join(plotdir, fname), dpi=150, bbox_inches='tight', metadata=pdf_metadata())
        plt.clf()


def plot_ratio_pu9_to_u5(energy_range):
    """Plots of evaluated ratios Pu9/U5 (n,f)."""
    ratio_dic = {}
    common_en = None 
    for dbname, gmadb in gmadbs.items():
        curdf = gmadb.get_datatable()
        pu9_sel = (curdf.REAC == 'MT:1-R1:9') & (curdf.NODE.str.match('xsid_'))
        u5_sel = (curdf.REAC == 'MT:1-R1:8') & (curdf.NODE.str.match('xsid_'))
        cur_pu9_en = curdf.loc[pu9_sel, 'ENERGY'].to_numpy() 
        cur_pu9_xs = curdf.loc[pu9_sel, 'POST'].to_numpy()
        cur_u5_en = curdf.loc[u5_sel, 'ENERGY'].to_numpy()
        cur_u5_xs = curdf.loc[u5_sel, 'POST'].to_numpy()
        cur_en = sorted(tuple(set(cur_pu9_en).intersection(set(cur_u5_en))))
        if common_en is not None and not np.all(np.array(common_en) == np.array(cur_en)):
            raise ValueError('mismatching energy meshes')
        common_en = np.array(cur_en)
        cur_u5_xs = [xs for en, xs in zip(cur_u5_en, cur_u5_xs) if en in cur_en]
        cur_pu9_xs = [xs for en, xs in zip(cur_pu9_en, cur_pu9_xs) if en in cur_en]
        ratio_dic[dbname] = np.array(cur_pu9_xs) / np.array(cur_u5_xs)

    for dbname, curratio in ratio_dic.items():
        curlabel = dbname.replace('POST_','').replace('data_', 'data_feb2022_')
        if curlabel == 'data':
            curlabel = 'data_feb2022'
        curratio = ratio_dic[dbname] / ratio_dic['data2017']
        plt.plot(common_en, curratio, label=curlabel)
        
    plt.legend(loc='upper right', prop={'size': 6})
    plt.xlim(energy_range)
    plt.ylim([0.98, 1.02])
    plt.xlabel('energy [MeV]')
    plt.ylabel('ratio PU9/U5(n,f) relative to std2017')
    fname = 'ratio_pu9_to_u5_comparisons' + '_from_' + str(energy_range[0]) + '_to_' + str(energy_range[1]) + '.pdf'
    plt.savefig(os.path.join(plotdir, fname), dpi=150, bbox_inches='tight', metadata=pdf_metadata())
    plt.clf()


def plot_sacs_table():
    curdb = gmadbs['data_with_mannhart_sacs'].get_datatable()
    curdf = gmadbs['data_with_mannhart_sacs'].get_datatable()
    reac_descr = curdf[curdf.NODE.str.match('xsid_')].groupby('NODE').agg({'DESCR': 'first'})
    reac_descr.index = reac_descr.index.str.replace('xsid_','')
    reac_descr.index = np.array(reac_descr.index, dtype=int)
    reac_descr.sort_index(inplace=True)
    sacs_reacs = curdf.loc[curdf.REAC.str.match('MT:6-')
            | curdf.REAC.str.match('MT:10-'), 'REAC'].unique()

    descr_dic = {k: reac_descr.loc[int(re.search('.*-R1:([0-9]+)', k).group(1)), 'DESCR']
            for k in sacs_reacs if k.startswith('MT:6-')}
    descr_dic.update({k: ' / '.join([reac_descr.loc[
            int(re.search('.*-R1:([0-9]+)-R2:([0-9]+)', k).group(i)), 'DESCR'
        ] for i in range(1,3)]) for k in sacs_reacs if k.startswith('MT:10-')})
    descr_dic = {k: v + ' SACS' for k, v in descr_dic.items()}
    # extend the data
    cur_id = 2700
    pseudo_exp_list = []
    for reacstr, descrstr in descr_dic.items():
        curexp = {}
        curexp['NODE'] = 'exp_' + str(cur_id)
        curexp['REAC'] = reacstr
        curexp['DESCR'] = descrstr
        cur_id += 1
        pseudo_exp_list.append(curexp)

    pseudo_exp_df = pd.DataFrame.from_records(pseudo_exp_list)

    extdfs = {}
    compmap = CompoundMap()
    for dbname, curdb in gmadbs.items(): 
        curdf = curdb.get_datatable() 
        extcurdf = pd.concat([curdf, pseudo_exp_df], ignore_index=True)
        curprop = compmap.propagate(extcurdf, extcurdf['POST'].to_numpy())  
        extcurdf['POST'] = curprop
        extdfs[dbname] = extcurdf

    for dbname, curdf in extdfs.items():
        pseudo_exp_df[dbname] = curdf.loc[curdf.NODE.str.match('exp_270.'), 'POST'].to_numpy()

    pseudo_exp_df.to_csv(os.path.join(plotdir, 'sacs_table.csv'), header=True, index=False)



reacstrs = ['MT:1-R1:8', 'MT:1-R1:9', 'MT:1-R1:10']
create_xs_to_ref_plots([0.1, 5], [0.99, 1.01], reacstrs)
create_xs_to_ref_plots([13, 15], [0.98, 1.02], reacstrs)
plot_ratio_pu9_to_u5([0.1, 5])
plot_ratio_pu9_to_u5([13, 15])
create_uncertainty_plots([0.1, 5], [0.004, 0.01], reacstrs) 
create_uncertainty_plots([13, 15], [0.004, 0.01], reacstrs) 
plot_sacs_table()
