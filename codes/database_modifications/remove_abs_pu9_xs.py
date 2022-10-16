from gmapi.data_management.datablock_list import DatablockList


def apply(datablock_list):
    remove_dsids = []
    # impact of removing abs Pu9 xs large (0.7%); removing maybe justified
    # impact of removing abs U5 small (0.3%); removing not justified
    for db in datablock_list:
        for ds in db['datasets']:
            if ds['MT'] == 1 and ds['NT'][0] in (9,):
                remove_dsids.append(ds['NS'])

    dblist = DatablockList(datablock_list)
    if len(remove_dsids) > 0:
        dblist.remove_datasets(remove_dsids)
    datablock_list = dblist.get_datablock_list(dict)
    return datablock_list
