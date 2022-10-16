# cf252_dat2022.txt contains the SACS and SACS ratios
# as provided by Roberto per email on 26 September 2022

import importlib
import argparse
import os
import numpy as np
import pandas as pd
from copy import deepcopy
import json
import subprocess
import sys
sys.path.insert(0, os.path.join('codes', 'database_modifications'))

parser = argparse.ArgumentParser()
parser.add_argument('--dbname', type=str)
parser.add_argument('--keep_dummy', action='store_true')
parser.add_argument('--ops', type=str, nargs='*', default=[])
parser.add_argument('--gmapi_rev', type=str)
args = parser.parse_args()


dbname = args.dbname
keep_dummy = args.keep_dummy
gmapi_rev = args.gmapi_rev
ops = args.ops

print('---- modifications to database ----')
print('root database: ' + str(dbname))
print('keep dummy datasets: ' + str(keep_dummy))
print('sequence of modifications: ')
for curop in ops:
    print('  - ' + curop)
print('-----------------------------------')

# check out the desired gmapy version
subprocess.check_call(["git", "checkout", gmapi_rev], cwd="codes/gmapy")
import sys
sys.path.insert(0, 'codes/gmapy')
import gmapi
from gmapi.data_management.database_IO import read_gma_database
from gmapi.data_management.dataset import Dataset
from gmapi.data_management.datablock import Datablock
from gmapi.data_management.datablock_list import DatablockList
from gmapi.legacy.conversion_utils import NumpyEncoder
from gmapi.mappings.priortools import remove_dummy_datasets

datafile = os.path.join('database', dbname + '.json')
db_dic = read_gma_database(datafile)
datablock_list = db_dic['datablock_list']
if not keep_dummy:
    remove_dummy_datasets(datablock_list)

for curop in ops:
    print('applying ' + curop)
    curop_module = importlib.import_module(curop)
    datablock_list = curop_module.apply(datablock_list)

new_db_dic = {
    'prior': db_dic['prior_list'],
    'datablocks': datablock_list
}

with open('database/testdata.json', 'w') as f:
    json.dump(new_db_dic, f, indent=4, cls=NumpyEncoder)
