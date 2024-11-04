

from numpy import loadtxt
from known import Table
from .import DB_UID, DB_NAME, DB_PASS, DB_ACCESS
from .import DEFAULT_ACCESS, DEFAULT_PASS, DEFAULT_ACCESS_ADMIN, DEFAULT_PASS_ADMIN
from .import CELL_DELIM, ROW_DELIM

def build_new(
        out_csv,
        *info_cols
):
    header = (DB_ACCESS, DB_UID, DB_NAME, *info_cols, DB_PASS) #<----- SCHEMA
    headerset = set(header)
    assert len(headerset)==len(header), f'Header has duplicate columns'


    # create a new table 
    logindb = Table.Create(
        columns = header,  
        primary_key = DB_UID, 
        cell_delimiter=CELL_DELIM, 
        record_delimiter=ROW_DELIM,
    )
    # write to disk\
    import getpass
    from sys import platform as this_platform
    this_user = getpass.getuser()
    logindb[this_user] = [DEFAULT_ACCESS_ADMIN, this_user, this_platform ] + ['' for _ in info_cols] + [DEFAULT_PASS_ADMIN]
    logindb > f'{out_csv}'
    del logindb
    return this_user, this_platform

def build_from_csv(
        in_csv,     # name of input csv file - supposed to have header and at least one row
        uid_col,    #  name of col to be used as unique identifier
        name_col,   #  name of col to be used as friendly name (alias)
        out_csv,    #  name of output csv file
        ):
    r"""Build a Table from a csv file - 
        the csv must contain the uid and name col, 
        access token and password are set to default
    """
    users = loadtxt(in_csv, dtype='str', delimiter=CELL_DELIM)
    if users.ndim == 2: header, data = list(users[0]), users[1:]
    else:
        if users.ndim == 1: raise AssertionError(f'Input file has no rows (require at least one)')
        else:               raise AssertionError(f'Unexpected number of dims {users.ndim}, expected 2')
    
    headerset = set(header)
    assert len(headerset)==len(header), f'Header has duplicate columns'

    # exists cols
    assert uid_col in headerset, f'Specified {DB_UID} column "{uid_col}" not found in header'
    assert name_col in headerset, f'Specified {DB_NAME} column "{name_col}" not found in header'

    info_cols = [*header]
    info_cols.remove(uid_col)
    info_cols.remove(name_col)
    assert len(set(info_cols).intersection(set( [DB_ACCESS, DB_NAME, DB_PASS, DB_UID] )))==0, f'Inbuilt column names not allowed'

    # header-mapping
    headermap = {n:i for i,n in enumerate(header)}
    iuid, iname = headermap[uid_col] , headermap[name_col] 

    # check if all uids are unique
    all_uids = data[:, iuid]
    all_uids_set = set(all_uids)
    assert len(all_uids) == len(all_uids_set), f'Duplicate {DB_UID}s exists'

    # create a new table 
    logindb = Table.Create(
        columns = (DB_ACCESS, DB_UID, DB_NAME, *info_cols, DB_PASS),  #<----- SCHEMA
        primary_key = DB_UID, 
        cell_delimiter=CELL_DELIM, 
        record_delimiter=ROW_DELIM,
    )
    # write to disk
    for row in data: logindb[row[iuid]] = [DEFAULT_ACCESS, row[iuid], row[iname] ] + [row[headermap[i]] for i in info_cols] + [DEFAULT_PASS]
    logindb > f'{out_csv}'
    del logindb
    return

def load_from_csv(in_csv): return Table.Import(f'{in_csv}', key_at=DB_UID, cell_delimiter=CELL_DELIM, record_delimiter=ROW_DELIM)

