import argparse
import subprocess
import sys
from save_result import save_result

dbfile = 'database/data2017.json'

parser = argparse.ArgumentParser()
parser.add_argument('--gmapi_rev', type=str)
parser.add_argument('--fix_ppp_bug', action='store_true')
args = parser.parse_args()

gmapi_rev = args.gmapi_rev
fix_ppp_bug = args.fix_ppp_bug

print('--- parameters ----')
print('gmapi_rev: ' + str(gmapi_rev))
print('fix_ppp_bug: ' + str(fix_ppp_bug))
print('-------------------')

# check out the desired gmapy version
subprocess.check_call(["git", "checkout", gmapi_rev], cwd="codes/gmapy")
sys.path.insert(0, 'codes/gmapy')
from gmapi.legacy.legacy_gmap import run_gmap;

res = run_gmap(dbfile=dbfile, dbtype="json",
               fix_ppp_bug=fix_ppp_bug, fix_sacs_jacobian=False,
               legacy_integration=True, legacy_output=False,
               correct_ppp=True, remove_dummy=False)

save_result(res, is_std2017=True, rel_to_std2017=False,
            fix_sacs_jacobian=False, legacy_integration=True)
