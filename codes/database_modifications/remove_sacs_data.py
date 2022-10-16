from gmapi.data_management.datablock_list import DatablockList


def apply(datablock_list):
    dblist = DatablockList(datablock_list)
    dblist.remove_datasets_by_mtnums([6,10])
    datablock_list = dblist.get_datablock_list(dict)
    return datablock_list
