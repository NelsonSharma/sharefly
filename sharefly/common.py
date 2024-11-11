
import os, importlib
from . import PYD, DSN

class Fake:
    def __len__(self): return len(self.__dict__)
    def __init__(self, **kwargs) -> None:
        for name, attribute in kwargs.items():  setattr(self, name, attribute)

class WorkSpace:

    def __init__(self):
        self.CWD = os.path.abspath(os.getcwd())
        self.PYD = PYD
        self.DSN = DSN

    def create(self, path):
        if not path: path = self.CWD
        path = os.path.abspath(path)
        try: os.makedirs(path, exist_ok=True)
        except: path = None
        self.path = path #<---- self.path
        return self

    def load(self, settings):
        self.settings = None
        self.settings_path = None
        if self.path: 
            if settings:
                settings_file = f'{settings}.py' # the name of configs file
                settings_path = os.path.join(self.path, settings_file) # should exsist under workdir
                if not os.path.isfile(settings_path):
                    try:
                        with open(os.path.join(self.PYD, f'{self.DSN}.py'), 'r') as r: 
                            with open(settings_path, 'w', encoding='utf-8') as w: w.write(r.read())
                    except: pass
                if os.path.isfile(settings_path):
                    try: # Load the module from the specified file path
                        c_spec = importlib.util.spec_from_file_location(settings, settings_path)
                        c_module = importlib.util.module_from_spec(c_spec)
                        c_spec.loader.exec_module(c_module)
                        self.settings = c_module
                        self.settings_path = settings_path
                    except: pass

        return self

    def get(self, name, do_call=False, as_dict=True):
        try: kv = getattr(self.settings, name)
        except: return None, False, f'Could not load {name} from module'
        if do_call and not isinstance(kv, dict): 
            try: kv=kv() # try to call it and see if it returns a dict (key-value pairs)
            except: pass
        if not isinstance(kv, dict): return None, False, f'Expecting a dict object but got {type(kv)}'
        if not as_dict: 
            try: kv = Fake(**kv)
            except: return None, False, f'Failed to convert from dict to object'
        return kv, True, f'Success loading {len(kv)} key-value pairs'



class Symbols:
    CORRECT =       '✓'
    INCORRECT =     '✗'
    TRI =           'Δ'
    DOT=            '●'
    SUN=            '⚙'
    ARROW1=         '↦'
    ARROW2=         '⇒'
    ARROW3=         '↪'
    CSV_DELIM =     ','
    SSV_DELIM =     '\n'


#-----------------------------------------------------------------------------------------
# Special Objects
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
class Table:

    @staticmethod
    def CreateData(*columns):
        data = {None:[f'{col}' for col in columns]} # this is to make sure that col names are always on top
        return data

    @staticmethod
    def Create(columns:tuple, primary_key:str, cell_delimiter=',', record_delimiter='\n'):
        # should be called on a new object after init\
        table = __class__()
        table.data = __class__.CreateData(*columns)
        table.pk = primary_key
        table.pkat = table.data[None].index(table.pk)
        table.cell_delimiter, table.record_delimiter = cell_delimiter, record_delimiter
        return table


    @staticmethod
    def ImportData(path, key_at, cell_delimiter, record_delimiter): 
        with open(path, 'r', encoding='utf-8') as f: 
            s = f.read()
            lines = s.split(record_delimiter)
            cols = lines[0].split(cell_delimiter) #<--- only if None:cols was added as a first entry (using Create method)
            data = {None:cols}
            if isinstance(key_at, str): key_at = cols.index(key_at)
            assert key_at>=0,f'Invlaid key {key_at}'
            for line in lines[1:]:
                if line:
                    cells = line.split(cell_delimiter)
                    data[f'{cells[key_at]}'] = cells
        return data
    
    @staticmethod
    def Import(path, key_at, cell_delimiter=',', record_delimiter='\n'): 
        table = __class__()
        table.data = __class__.ImportData(path, key_at, cell_delimiter, record_delimiter)
        if isinstance(key_at, str): key_at = table[None].index(key_at)
        table.pk = table.data[None][key_at]
        table.pkat = key_at
        table.cell_delimiter, table.record_delimiter = cell_delimiter, record_delimiter
        return table


    @staticmethod
    def ExportData(data, path, cell_delimiter, record_delimiter): 
        with open(path, 'w', encoding='utf-8') as f: 
            for v in data.values(): f.write(cell_delimiter.join(v)+record_delimiter)

    @staticmethod
    def Export(table, path): 
        __class__.ExportData(table.data, path, table.cell_delimiter, table.record_delimiter)

    # get row as dict
    def __call__(self, key): return {k:v for k,v in zip(self[None], self[key])}

    # get row as it is (list)
    def __getitem__(self, key): return self.data[key]

    # set row based on if its a dict or a list (note: key is irrelavant here)
    def __setitem__(self, key, row):
        assert len(row) == len(self[None]), f'Rows are expected to have length {len(self[None])} but got {len(row)}'
        if isinstance(row, dict):
            key = row[self.pk]
            if key is not None: self.data[f'{key}'] = [row[r] for r in self[None]]
        else: 
            key = row[self.pkat]
            if key is not None: self.data[f'{key}'] = list(row)

    # del row based on key
    def __delitem__(self, key):
        if key is not None: del self.data[key]

    def __contains__(self, key): return key in self.data

    # quick export > file
    def __gt__(self, other):__class__.ExportData(self.data, f'{other}', self.cell_delimiter, self.record_delimiter)

    # quick import < file
    def __lt__(self, other): self.data = __class__.ImportData(f'{other}', self.pkat, self.cell_delimiter, self.record_delimiter)

    # total number of rows
    def __len__(self): return len(self.data)-1

#-----------------------------------------------------------------------------------------

import sqlite3, re

class Database:
    # READ_ONLY CONSTANTS - do not change

    def SCHEMA(self): return f'''
            CREATE TABLE USERS (
                UID TEXT PRIMARY KEY NOT NULL CHECK (length(UID) <= {self.uid_max_len}),
                NAME TEXT NOT NULL CHECK (length(UID) <= {self.name_max_len}),
                TAG TEXT,
                EMAIL TEXT,
                ACCESS TEXT,
                PASS TEXT NOT NULL CHECK (length(UID) <= {self.password_max_len}),
            );'''

    def __init__(self,  policy):
        self.policy = Fake(**policy) if isinstance(policy, dict) else policy 

    @staticmethod
    def match(instr, pattern, length):  return \
        (len(instr) >= length[0]) and \
        (len(instr) <= length[-1]) and \
        (re.match(pattern, instr))
    
    def VALIDATE_PASS(self, instr):     return __class__.match(instr, self.policy.password_pattern, self.policy.password_length)
    def VALIDATE_UID(self, instr):      return __class__.match(instr, self.policy.uid_pattern,      self.policy.uid_length)
    def VALIDATE_NAME(self, instr):     return __class__.match(instr, self.policy.name_pattern,     self.policy.name_length)


    def connect(self, dbpath):
        self.connection = sqlite3.connect(dbpath)
        self.cursor = self.connection.cursor()
    
    def commit(self): self.connection.commit()

    def disconnect(self): self.connection.close()

    def create(self): self.cursor.execute(self.SCHEMA())
