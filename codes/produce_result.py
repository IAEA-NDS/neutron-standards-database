import argparse
import os
import subprocess
from save_result import save_result

dbdir = 'database'

parser = argparse.ArgumentParser()
parser.add_argument('--gmapi_rev', type=str)
parser.add_argument('--rel_to_std2017', action='store_true')
parser.add_argument('--correct_ppp', action='store_true')
parser.add_argument('--fix_sacs_jacobian', action='store_true')
parser.add_argument('--legacy_integration', action='store_true')
parser.add_argument('--maxiter', type=int, default=None)
parser.add_argument('--lmb', type=float, default=None)
parser.add_argument('--rtol', type=float)
parser.add_argument('--atol', type=float)
parser.add_argument('--no_reject', action='store_true')
parser.add_argument('--no_conv_req', action='store_true')
args = parser.parse_args()
rel_to_std2017 = args.rel_to_std2017
gmapi_rev = args.gmapi_rev
correct_ppp = args.correct_ppp
fix_sacs_jacobian = args.fix_sacs_jacobian
legacy_integration = args.legacy_integration

maxiter = args.maxiter
lmb = args.lmb
no_reject = args.no_reject
no_conv_req = args.no_conv_req
rtol = args.rtol
atol = args.atol
lm_args = {}
if maxiter is not None:
    lm_args['maxiter'] = maxiter
if lmb is not None:
    lm_args['lmb'] = lmb
lm_args['no_reject'] = no_reject
lm_args['must_converge'] = not no_conv_req
lm_args['rtol'] = rtol
lm_args['atol'] = atol

print('--- parameters for run ---')
print('gmapi_rev: ' + str(gmapi_rev))
print('fix_sacs_jacobian: ' + str(fix_sacs_jacobian))
print('correct_ppp: ' + str(correct_ppp))
print('legacy_integration: ' + str(legacy_integration))
print('rel_to_std2017: ' + str(rel_to_std2017))
print('maxiter: ' + str(lm_args['maxiter']))
print('lmb: ' + str(lm_args['lmb']))
print('rtol: ' + str(rtol))
print('atol: ' + str(atol))
print('no_reject: ' + str(lm_args['no_reject'])) 
print('must converge: ' + str(lm_args['must_converge']))
print('--------------------------')

# check out the desired gmapy version
subprocess.check_call(["git", "checkout", gmapi_rev], cwd="codes/gmapy")
import sys
sys.path.insert(0, 'codes/gmapy')
# load the gmapy modules
from gmapi import GMADatabase
from gmapi.mappings.compound_map import CompoundMap

compmap = CompoundMap(fix_sacs_jacobian=fix_sacs_jacobian,
                      legacy_integration=legacy_integration)
gmadb = GMADatabase(os.path.join(dbdir, 'testdata.json'), mapping=compmap)
gmadb.evaluate(correct_ppp=correct_ppp, **lm_args)

# create the result plot
df = gmadb.get_datatable()
res = {
    'table': df,
    'idcs': gmadb._cache['adj_idcs'],
    'postcov': gmadb.get_postcov(idcs=gmadb._cache['adj_idcs']).toarray()
    }

save_result(res, is_std2017=False,
            fix_sacs_jacobian=fix_sacs_jacobian,
            legacy_integration=legacy_integration,
            rel_to_std2017=rel_to_std2017)
