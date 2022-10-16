def apply(datablock_list):
    for db in datablock_list:
        for ds in db['datasets']:
            if (ds['MT'] == 3 and (
                (ds['NT'][0] == 9 and ds['NT'][1] in (8, 10)) or
                (ds['NT'][1] == 9 and ds['NT'][0] in (8, 10)))):
                ds['MT'] = 4
                print(f'teststring pu9: {ds["NS"]} - {ds["MT"]} : {ds["NT"]}')
    return datablock_list
