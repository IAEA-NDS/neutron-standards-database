def apply(datablock_list):
    for db in datablock_list:
        for ds in db['datasets']:
            if (ds['MT'] == 3 and (
                (ds['NT'][0] == 8 and ds['NT'][1] in (9,)) or
                (ds['NT'][1] == 8 and ds['NT'][0] in (9,)))):
                ds['MT'] = 4
                print(f'teststring u5: {ds["NS"]} - {ds["MT"]} : {ds["NT"]}')
    return datablock_list
