
__doc__=f""" 
-------------------------------------------------------------
sharefly - Flask based web app for sharing files and quiz evaluation
-------------------------------------------------------------

Install the required packages
    
    python -m pip install Flask Flask-WTF waitress nbconvert

Note: the `nbconvert` is optional - without it, the 'board' functionality will be missing

To strat the server use,

    python -m known.sharefly --dir=path/to/workspace

To stop the server, press control-c or send keyboard interupt signal

Note: default `configs.py` file will be created under workspace directory
-> the dict named `current` will be choosen as the config - it should be defined at the end of the file
-> a config name `default` will be created - it is used as a fall-back config

Edit the configs file which should be located at `path/to/workspace/configs.py`
Multiple configs can be defined in that single file, only the `current` variable will be used

-------------------------------------------------------------
Note:
special string "::::" is used for replacing javascript on `repass` - uid and url should not contain this
special username 'None' is not allowed however words like 'none' will work
rename argument means (0 = not allowed) (1 = only rename) (2 = rename and remoji)
-------------------------------------------------------------
"""






# user access is defined by a set of charaters
USER_ACCESS_DEF = {
    # >> case-sensetive
    '+'     :   'Allow Admin', # admin includes 'X'
    '-'     :   'Exclude from Evaluation',
    'D'     :   'Directory Access',
    'U'     :   'Allow Uploading',
    'S'     :   'Self-Uploads Access',
    'R'     :   'Self-Reports Access',
    'X'     :   'Allow Evaluation and Reset-Password',
    'B'     :   'Allow Reading Board',
    'P'     :   'Allow Posting on Board',
}

# Global Defaults
DEFAULT_ACCESS, DEFAULT_PASS = 'DURB', ''
DEFAULT_ACCESS_ADMIN, DEFAULT_PASS_ADMIN = '+-DUSRXBP', ''

DB_UID, DB_NAME, DB_PASS, DB_ACCESS = 'UID', 'NAME', 'PASS', 'ACCESS'
# DB_ACCESS[0] DB_UID[1] DB_NAME[2] ..... DB_PASS[-1]

CELL_DELIM, ROW_DELIM = ',', '\n'

#UID_JOIN = ""   # a string to join uids
#NAME_JOIN = " "  # a string to join names


#-----------------------------------------------------------------------------------------
# password policy
#-----------------------------------------------------------------------------------------
import re
MAX_STR_LEN = 50
#-----------------------------------------------------------------------------------------
def VALIDATE_PASS(instr):   # a function that can validate the password - returns bool type
    try: assert (len(instr) < MAX_STR_LEN) and bool(re.fullmatch("(\w|@|\.)+", instr)) # alpha_numeric @.
    except AssertionError: return False
    return True
#-----------------------------------------------------------------------------------------
# uid policy
def VALIDATE_UID(instr):   # a function that can validate the uid - returns bool type
    try: assert (len(instr) < MAX_STR_LEN) and bool(re.fullmatch("(\w)+", instr)) # alpha_numeric 
    except AssertionError: return False
    return True
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
# name policy
def VALIDATE_NAME(instr): return  (len(instr) >0) and (len(instr) < MAX_STR_LEN) and bool(re.fullmatch("((\w)(\w|\s)*(\w))|(\w)", instr)) # alpha-neumeric but no illegal spaces before or after
#-----------------------------------------------------------------------------------------











import time, random, datetime

def GET_SECRET_KEY():
    
    randx = lambda : random.randint(1111111111, 9999999999)
    rx = []
    for _ in range(4):
        sleep_for = abs(float(datetime.datetime.now().second -  random.randint(1, 30)) / 10.0)
        time.sleep(sleep_for)
        rx.append(str(randx()))
        for _ in range(datetime.datetime.now().microsecond%int(str(datetime.datetime.now().microsecond)[-1:-4])): _ = randx()
    return ':'.join(rx)









def DISPLAY_SIZE_READABLE(mus):
    # find max upload size in appropiate units
    mus_kb = mus/(2**10)
    if len(f'{int(mus_kb)}') < 4:
        mus_display = f'{mus_kb:.2f} KB'
    else:
        mus_mb = mus/(2**20)
        if len(f'{int(mus_mb)}') < 4:
            mus_display = f'{mus_mb:.2f} MB'
        else:
            mus_gb = mus/(2**30)
            if len(f'{int(mus_gb)}') < 4:
                mus_display = f'{mus_gb:.2f} GB'
            else:
                mus_tb = mus/(2**40)
                mus_display = f'{mus_tb:.2f} TB'
    return mus_display


def NEW_NOTEBOOK_STR(title, nbformat=4, nbformat_minor=2):
    return '{"cells": [{"cell_type": "markdown","metadata": {},"source": [ "'+str(title)+'" ] } ], "metadata": { }, "nbformat": '+str(nbformat)+', "nbformat_minor": '+str(nbformat_minor)+'}'





#-----------------------------------------------------------------------------------------
# Special Objects
#-----------------------------------------------------------------------------------------
class Fake:
    def __len__(self): return len(self.__dict__)
    def __init__(self, **kwargs) -> None:
        for name, attribute in kwargs.items():  setattr(self, name, attribute)
#-----------------------------------------------------------------------------------------

def str2bytes(size):
    sizes = dict(KB=2**10, MB=2**20, GB=2**30, TB=2**40)
    return int(float(size[:-2])*sizes.get(size[-2:].upper(), 0))

class FileValidator:

    def __init__(self, args_ext, args_required):
                
        self.ALLOWED_EXTENSIONS = set([x.strip() for x in args_ext.split(',') if x])  # a set or list of file extensions that are allowed to be uploaded 
        if '' in self.ALLOWED_EXTENSIONS: self.ALLOWED_EXTENSIONS.remove('')
        def GET_VALID_RE_PATTERN(validext):
            if not validext: return ".+"
            pattern=""
            for e in validext: pattern+=f'{e}|'
            return pattern[:-1]
        self.VALID_FILES_PATTERN = GET_VALID_RE_PATTERN(self.ALLOWED_EXTENSIONS)
        self.REQUIRED_FILES = set([x.strip() for x in args_required.split(',') if x])  # a set or list of file extensions that are required to be uploaded 
        if '' in self.REQUIRED_FILES: self.REQUIRED_FILES.remove('')


    def __call__(self, filename):   # a function that checks for valid file extensions based on ALLOWED_EXTENSIONS
        if '.' in filename: 
            name, ext = filename.rsplit('.', 1)
            safename = f'{name}.{ext.lower()}'
            if self.REQUIRED_FILES:  isvalid = (safename in self.REQUIRED_FILES)
            else:               isvalid = bool(re.fullmatch(f'.+\.({self.VALID_FILES_PATTERN})$', safename))
        else:               
            name, ext = filename, ''
            safename = f'{name}'
            if self.REQUIRED_FILES:  isvalid = (safename in self.REQUIRED_FILES)
            else:               isvalid = (not self.ALLOWED_EXTENSIONS)
        return isvalid, safename


# ******************************************************************************************
