import os
from gmapi import GMADatabase
import matplotlib.pyplot as plt

dbdir='../database'
dbnames = [
    'data2017',
    'data2017_without_sacs',
    'data2017_with_mannhart_sacs',
    'data',
    'data_without_sacs',
    'data_with_mannhart_sacs'
    ]

gmadbs = {
    nm: GMADatabase(os.path.join(dbdir, nm + '.json'))
        for nm in dbnames
    }

for k, gmadb in gmadbs.items():
    print('evaluating ' + k)
    gmadb.evaluate(correct_ppp=True)

# some easy checks
# - without sacs does not contain sacs
# - with mannhart sacs contains sacs 
curdb = gmadbs['data2017_without_sacs']
curdf = curdb.get_datatable()
curdf[curdf.MT.str.match(





gmadb.evaluate()


df = gmadb.get_datatable()


# select a cross section
# plot it


# example to select the evaluaed xs
reddf = df[df.REAC.str.match('MT:1-R1:8') & 
           df.NODE.str.match('xsid_')]

# example how o select the experimental data
expdf = df[df.REAC.str.match('MT:1-R1:8') &
           df.NODE.str.match('exp_')]



energy = reddf.ENERGY.to_numpy()
xs = reddf.POST.to_numpy()

plt.title('test title') 
plt.xlabel('xlabel')
plt.ylabel('ylabel')
plt.plot(energy, xs)
plt.xlim([1,5])
plt.ylim([1,1.4])

# plot data with errorbar
energy = expdf.ENERGY.to_numpy() 
xs = expdf.DATA.to_numpy() 
plt.scatter(energy, xs, color='b', marker='o')


plt.show()




