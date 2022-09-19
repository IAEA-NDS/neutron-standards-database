import os
import numpy as np
import pandas as pd
from copy import deepcopy
import json
import gmapi
from gmapi.data_management.database_IO import read_gma_database
from gmapi.data_management.dataset import Dataset
from gmapi.data_management.datablock import Datablock
from gmapi.data_management.datablock_list import DatablockList
from gmapi.legacy.conversion_utils import NumpyEncoder


# define all the SACS measurements

mannhart_sacs_datablock = Datablock() 

ds = Dataset()
ds.define_metadata(2500, 1976, 'Heaton U5nf')
ds.define_quantity(6, [8])
ds.define_measurements([1.], [1.216])
ds.add_norm_uncertainty(1.62)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2501, 100, 'Grundl-William U5nf/U8nf')
ds.define_quantity(10, [8,10])
ds.define_measurements([1.], [3.73])
ds.add_norm_uncertainty(1.2)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2504, 100, 'Gundl-Gilliam U5f/Pu9f')
ds.define_quantity(10, [8,9])
ds.define_measurements([1.], [0.666])
ds.add_norm_uncertainty(0.9)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2505, 1976, 'Heaton Pu9f/U5f')
ds.define_quantity(10, [9,8])
ds.define_measurements([1.], [1.5])
ds.add_norm_uncertainty(1.6)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2506, 1976, 'Heaton U8f/U5f')
ds.define_quantity(10, [10,8])
ds.define_measurements([1.], [0.2644])
ds.add_norm_uncertainty(1.32)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2507, 1985, 'Schroeder U8f/U5f')
ds.define_quantity(10, [10,8])
ds.define_measurements([1.], [0.269])
ds.add_norm_uncertainty(1.2)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2508, 1985, 'Schroeder Pu9f/U5f')
ds.define_quantity(10, [9,8])
ds.define_measurements([1.], [1.5])
ds.add_norm_uncertainty(0.8)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2509, 1985, 'Schroeder U5f')
ds.define_quantity(6, [8])
ds.define_measurements([1.], [1.234])
ds.add_norm_uncertainty(1.45)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2510, 1985, 'Schroeder U8f')
ds.define_quantity(6, [10])
ds.define_measurements([1.], [0.332])
ds.add_norm_uncertainty(1.5)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2511, 1985, 'Schroeder Pu9f')
ds.define_quantity(6, [9])
ds.define_measurements([1.], [1.844])
ds.add_norm_uncertainty(1.3)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2512, 1978, 'Knoll U5f')
ds.define_quantity(6, [8])
ds.define_measurements([1.], [1.215])
ds.add_norm_uncertainty(1.79)
mannhart_sacs_datablock.add_datasets(ds)

ds = Dataset()
ds.define_metadata(2513, 1978, 'Knoll Pu9')
ds.define_quantity(6, [9])
ds.define_measurements([1.], [1.79])
ds.add_norm_uncertainty(2.26)
mannhart_sacs_datablock.add_datasets(ds)

# define the correlation matrix
tmp = np.array([
[ 100,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],      #   1    Grundl memo ABS (rev. Heaton)
[  23, 100,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0],      #   2    Grundl/Gilliam ratio
[  -9,  15, 100,   0,   0,   0,   0,   0,   0,   0,   0,   0],      #   4    Grundl/Gilliam ratio
[   0,   0,   0, 100,   0,   0,   0,   0,   0,   0,   0,   0],      #   5    Heaton ratio
[   0,   0,   0,  60, 100,   0,   0,   0,   0,   0,   0,   0],      #   6    Heaton ratio
[   0,   0,   0,   0,   0, 100,   0,   0,   0,   0,   0,   0],      #   7    Schroeder ratio
[   0,   0,   0,   0,   0,  77, 100,   0,   0,   0,   0,   0],      #   8    Schroeder ratio
[   0,   0,   0,   0,   0,   0,   0, 100,   0,   0,   0,   0],      #   9    Schroeder ABS
[   0,   0,   0,   0,   0,   0,   0,  50, 100,   0,   0,   0],      #  10    Schroeder ABS
[   0,   0,   0,   0,   0,   0,   0,  50,  50, 100,   0,   0],      #  11    Schroeder ABS
[   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 100,   0],      #  12    Davis/Knoll abs
[   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  59, 100]       #  13    Davis/Knoll
])
# make the covariance matrix symmetric
cormat = (tmp + tmp.T) / 1e2
np.fill_diagonal(cormat, 1)
mannhart_sacs_datablock.define_correlation_matrix(cormat)

# check it
np.sqrt(mannhart_sacs_datablock.get_covariance_matrix(unit='percent').toarray().diagonal())
mannhart_sacs_datablock.get_correlation_matrix()


# helpfer functions
def remove_sacs_data(datablock_list):
    dblist = DatablockList(datablock_list)
    dblist.remove_datasets_by_mtnums([6,10])
    datablock_list = dblist.get_datablock_list(dict)
    return datablock_list

def add_mannhart_sacs(datablock_list):
    dblist = DatablockList(datablock_list)
    dblist.remove_datasets_by_mtnums([6,10])
    dblist.add_datablock(mannhart_sacs_datablock)
    datablock_list = dblist.get_datablock_list(dict)
    return datablock_list


# following we create several variations of the
# standards 2017 and current data.gma file:
#   - all SACS removed
#   - with SACS and ratio of SACS data as used by Mannhart

datafiles = [
    '../database/data.json',
    '../database/data2017.json',
]

ops = [
    remove_sacs_data,
    add_mannhart_sacs
]

file_suffix = [
    '_without_sacs',
    '_with_mannhart_sacs'
]


for curdatafile in datafiles:
    for curop, cursuffix in zip(ops, file_suffix): 
        db_dic = read_gma_database(curdatafile)
        new_datablock_list = curop(db_dic['datablock_list'])
        new_db_dic = {
                'prior': db_dic['prior_list'],
                'datablocks': new_datablock_list
                }
        splitfn = os.path.splitext(curdatafile)
        new_filename = splitfn[0] + cursuffix + splitfn[1] 
        with open(new_filename, 'w') as f:
            json.dump(new_db_dic, f, indent=4, cls=NumpyEncoder)

