__doc__=f""" 
-------------------------------------------------------------
ShareFly - Flask-based web app for sharing files 
-------------------------------------------------------------
"""
#-----------------------------------------------------------------------------------------
from sys import exit
if __name__!='__main__': exit(f'[!] can not import {__name__}.{__file__}')
#-----------------------------------------------------------------------------------------

#%% [PRE-INITIALIZATION] @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 

import argparse
# ------------------------------------------------------------------------------------------
# args parsing
# ------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--dir', type=str, default='', help="path of workspace directory")
parser.add_argument('--verbose', type=int, default=2, help="verbose level in logging")
parser.add_argument('--log', type=str, default='', help="path of log dir - keep blank to disable logging")
parser.add_argument('--logname', type=str, default='sharefly_%Y_%m_%d_%H_%M_%S_%f_log.txt', help="name of logfile as formated string (works when logging is enabled)")
parser.add_argument('--con', type=str, default='', help="config name - if not provided, uses 'default'")
parser.add_argument('--reg', type=str, default='', help="if specified, allow users to register with specified access string such as DABU or DABUS+")
parser.add_argument('--cos', type=int, default=1, help="use 1 to create-on-start - create (overwrites) pages")
parser.add_argument('--coe', type=int, default=0, help="use 1 to clean-on-exit - deletes pages")
parser.add_argument('--access', type=str, default='', help="if specified, allow users to add access string such as DABU or DABUS+")
parser.add_argument('--msl', type=int, default=100, help="Max String Length for UID/NAME/PASSWORDS")
parser.add_argument('--eip', type=int, default=1, help="Evaluate Immediate Persis. If True, persist the eval-db after each single evaluation (eval-db in always persisted after update from template)")
parsed = parser.parse_args()
# ------------------------------------------------------------------------------------------
# imports
# ------------------------------------------------------------------------------------------
import os, re, getpass, random, logging, importlib.util
from io import BytesIO
from math import inf
import datetime
def fnow(format): return datetime.datetime.strftime(datetime.datetime.now(), format)
try:
    from flask import Flask, render_template, request, redirect, url_for, session, abort, send_file
    from flask_wtf import FlaskForm
    from wtforms import SubmitField, MultipleFileField
    from werkzeug.utils import secure_filename
    from wtforms.validators import InputRequired
    from waitress import serve
except: exit(f'[!] The required Flask packages missing:\tFlask>=3.0.2, Flask-WTF>=1.2.1\twaitress>=3.0.0\n  ⇒ pip install Flask Flask-WTF waitress')
try: 
    from nbconvert import HTMLExporter 
    has_nbconvert_package=True
except:
    print(f'[!] IPYNB to HTML rending will not work since nbconvert>=7.16.2 is missing\n  ⇒ pip install nbconvert')
    has_nbconvert_package = False
# ------------------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------------------
LOGDIR = f'{parsed.log}' # define log dir - contains all logs
LOGFILE = None
if LOGDIR and parsed.verbose>0: 
    LOGFILENAME = f'{fnow(parsed.logname)}'
    if not LOGFILENAME: exit(f'[!] Provided logfile nameLogging directory was not found and could not be created is blank!')
    try: os.makedirs(LOGDIR, exist_ok=True)
    except: exit(f'[!] Logging directory was not found and could not be created')
# ------------------------------------------------------------------------------------------
    try:# Set up logging to a file # also output to the console
        LOGFILE = os.path.join(LOGDIR, LOGFILENAME)
        logging.basicConfig(filename=LOGFILE, level=logging.INFO, format='%(asctime)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(console_handler)
    except: exit(f'[!] Logging could not be setup at {LOGFILE}')
# ------------------------------------------------------------------------------------------
# verbose level
# ------------------------------------------------------------------------------------------
if parsed.verbose==0: # no log
    def sprint(msg): pass
    def dprint(msg): pass
    def fexit(msg): exit(msg)
elif parsed.verbose==1: # only server logs
    if LOGFILE is None:
        def sprint(msg): print(msg) 
        def dprint(msg): pass 
        def fexit(msg): exit(msg)
    else:
        def sprint(msg): logging.info(msg) 
        def dprint(msg): pass 
        def fexit(msg):
            logging.error(msg) 
            exit()
elif parsed.verbose>=2: # server and user logs
    if LOGFILE is None:
        def sprint(msg): print(msg) 
        def dprint(msg): print(msg) 
        def fexit(msg): exit(msg)
    else:
        def sprint(msg): logging.info(msg) 
        def dprint(msg): logging.info(msg) 
        def fexit(msg):
            logging.error(msg) 
            exit()
else: raise ZeroDivisionError # impossible
# ------------------------------------------------------------------------------------------


#%% [INITIALIZATION] @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 
# ------------------------------------------------------------------------------------------
sprint(f'Starting...')
sprint(f'↪ Logging @ {LOGFILE}')
# ------------------------------------------------------------------------------------------
# workdir
#-----------------------------------------------------------------------------------------
WORKDIR = f'{parsed.dir}' # define working dir - contains all bases
if not WORKDIR: WORKDIR = os.getcwd()
WORKDIR=os.path.abspath(WORKDIR)
try: os.makedirs(WORKDIR, exist_ok=True)
except: fexit(f'[!] Workspace directory was not found and could not be created')
sprint(f'↪ Workspace directory is {WORKDIR}')
#-----------------------------------------------------------------------------------------
# globals
#-----------------------------------------------------------------------------------------
CSV_DELIM = ','
SSV_DELIM = '\n'
NEWLINE = '\n'
TABLINE = '\t'
LOGIN_ORD = ['ADMIN','UID','NAME','PASS']
LOGIN_ORD_MAPPING = {v:i for i,v in enumerate(LOGIN_ORD)}
EVAL_ORD = ['UID', 'NAME', 'SCORE', 'REMARK', 'BY']
DEFAULT_USER = 'admin'
DEFAULT_ACCESS = f'DABUSRX+-'

MAX_STR_LEN = int(parsed.msl) if parsed.msl>0 else 1
def rematch(instr, pattern):  return \
    (len(instr) >= 0) and \
    (len(instr) <= MAX_STR_LEN) and \
    (re.match(pattern, instr))

def VALIDATE_PASS(instr):     return rematch(instr, r'^[a-zA-Z0-9~!@#$%^&*()_+{}<>?`\-=\[\].]+$')
def VALIDATE_UID(instr):      return rematch(instr, r'^[a-zA-Z0-9._@]+$') and instr[0]!="."
def VALIDATE_NAME(instr):     return rematch(instr, r'^[a-zA-Z0-9]+(?: [a-zA-Z0-9]+)*$')

def DICT2CSV(path, d, ord):
    with open(path, 'w', encoding='utf-8') as f: 
        f.write(CSV_DELIM.join(ord)+SSV_DELIM)
        for v in d.values(): f.write(CSV_DELIM.join(v)+SSV_DELIM)

def DICT2BUFF(d, ord):
    b = BytesIO()
    b.write(f'{CSV_DELIM.join(ord)+SSV_DELIM}'.encode(encoding='utf-8'))
    for v in d.values(): b.write(f'{CSV_DELIM.join(v)+SSV_DELIM}'.encode(encoding='utf-8'))
    b.seek(0)
    return b

def S2DICT(s, key_at):
    lines = s.split(SSV_DELIM)
    d = dict()
    for line in lines[1:]:
        if line:
            cells = line.split(CSV_DELIM)
            d[f'{cells[key_at]}'] = cells
    return d

def CSV2DICT(path, key_at):
    with open(path, 'r', encoding='utf-8') as f: s = f.read()
    return S2DICT(s, key_at)

def BUFF2DICT(b, key_at):
    b.seek(0)
    return S2DICT(b.read().decode(encoding='utf-8'), key_at)

def GET_SECRET_KEY(postfix):
    randx = lambda : random.randint(1111111111, 9999999999)
    r1 = randx()
    for _ in range(datetime.datetime.now().microsecond % 60): _ = randx()
    r2 = randx()
    for _ in range(datetime.datetime.now().second): _ = randx()
    r3 = randx()
    for _ in range(datetime.datetime.now().minute): _ = randx()
    r4 = randx()
    return ':{}:{}:{}:{}:{}:'.format(r1,r2,r3,r4,postfix)

def READ_DB_FROM_DISK(path, key_at):
    try:    return CSV2DICT(path, key_at), True
    except: return dict(), False

def WRITE_DB_TO_DISK(path, db_frame, ord): # will change the order
    try:
        DICT2CSV(path, db_frame, ord) # save updated login information to csv
        return True
    except PermissionError:
        return False

def GET_FILE_LIST (d): 
    dlist = []
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p): dlist.append(f)
    return sorted(dlist)

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

class Fake:
    def __len__(self): return len(self.__dict__)
    def __init__(self, **kwargs) -> None:
        for name, attribute in kwargs.items():  setattr(self, name, attribute)
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# ==> read configurations
#-----------------------------------------------------------------------------------------
CONFIG = parsed.con if parsed.con else 'default' # the config-dict to read from
CONFIG_MODULE = '__configs__'  # the name of configs module
CONFIGS_FILE = f'{CONFIG_MODULE}.py' # the name of configs file
# try to import configs
CONFIGS_FILE_PATH = os.path.join(WORKDIR, CONFIGS_FILE) # should exsist under workdir
if not os.path.isfile(CONFIGS_FILE_PATH):
    sprint(f'↪ Creating default config "{CONFIGS_FILE}" ...')
    try: 
        from . import DEFAULT_CONFIG
        DEFAULT_CONFIG(CONFIGS_FILE_PATH)
        del DEFAULT_CONFIG
    except: fexit(f'[!] Could find or create config "{CONFIG_MODULE}" at "{CONFIGS_FILE_PATH}"')
try: 
    # Load the module from the specified file path
    c_spec = importlib.util.spec_from_file_location(CONFIG_MODULE, CONFIGS_FILE_PATH)
    c_module = importlib.util.module_from_spec(c_spec)
    c_spec.loader.exec_module(c_module)
    sprint(f'↪ Imported config-module "{CONFIG_MODULE}" from {c_module.__file__}')
except: fexit(f'[!] Could import configs module "{CONFIG_MODULE}" at "{CONFIGS_FILE_PATH[:-3]}"')
try:
    sprint(f'↪ Reading config from {CONFIG_MODULE}.{CONFIG}')
    if "." in CONFIG: 
        CONFIGX = CONFIG.split(".")
        config_dict = c_module
        while CONFIGX:
            m = CONFIGX.pop(0).strip()
            if not m: continue
            config_dict = getattr(config_dict, m)
    else: config_dict = getattr(c_module, CONFIG)
except:
    fexit(f'[!] Could not read config from {CONFIG_MODULE}.{CONFIG}')

if not isinstance(config_dict, dict): 
    try: config_dict=config_dict()
    except: pass
if not isinstance(config_dict, dict): raise fexit(f'Expecting a dict object for config')

try: 
    sprint(f'↪ Building config from {CONFIG_MODULE}.{CONFIG}')
    args = Fake(**config_dict)
except: fexit(f'[!] Could not read config')
if not len(args): fexit(f'[!] Empty or Invalid config provided')

#-----------------------------------------------------------------------------------------
# Directories
#-----------------------------------------------------------------------------------------
HTMLDIR = ((os.path.join(WORKDIR, args.html)) if args.html else WORKDIR)
try: os.makedirs(HTMLDIR, exist_ok=True)
except: fexit(f'[!] HTML directory was not found and could not be created')
sprint(f'⚙ HTML Directory @ {HTMLDIR}')

BASEDIR = ((os.path.join(WORKDIR, args.base)) if args.base else WORKDIR)
try:     os.makedirs(BASEDIR, exist_ok=True)
except:  fexit(f'[!] base directory  @ {BASEDIR} was not found and could not be created') 
sprint(f'⚙ Base Directory: {BASEDIR}')

# ------------------------------------------------------------------------------------------
# WEB-SERVER INFORMATION
# ------------------------------------------------------------------------------------------\
if not args.secret: 
    APP_SECRET_KEY =  GET_SECRET_KEY(fnow("%Y%m%d%H%M%S"))
    sprint(f'⇒ secret not provided - using random secret')
else:
    APP_SECRET_KEY_FILE = os.path.join(BASEDIR, args.secret)
    if not os.path.isfile(APP_SECRET_KEY_FILE): #< --- if key dont exist, create it
        APP_SECRET_KEY =  GET_SECRET_KEY(fnow("%Y%m%d%H%M%S"))
        try:
            with open(APP_SECRET_KEY_FILE, 'w') as f: f.write(APP_SECRET_KEY) #<---- auto-generated key
        except: fexit(f'[!] could not create secret key @ {APP_SECRET_KEY_FILE}')
        sprint(f'⇒ New secret created: {APP_SECRET_KEY_FILE}')
    else:
        try:
            with open(APP_SECRET_KEY_FILE, 'r') as f: APP_SECRET_KEY = f.read()
            sprint(f'⇒ Loaded secret file: {APP_SECRET_KEY_FILE}')
        except: fexit(f'[!] could not read secret key @ {APP_SECRET_KEY_FILE}')

# ------------------------------------------------------------------------------------------
# LOGIN DATABASE - CSV
# ------------------------------------------------------------------------------------------
if not args.login: fexit(f'[!] login file was not provided!')    
LOGIN_XL_PATH = os.path.join( BASEDIR, args.login) 
if not os.path.isfile(LOGIN_XL_PATH): 
    sprint(f'⇒ Creating new login file: {LOGIN_XL_PATH}')
    
    this_user = getpass.getuser()
    if not (VALIDATE_UID(this_user)):  this_user=DEFAULT_USER

    
    try:this_name = os.uname().nodename
    except:this_name = ""
    if not (VALIDATE_NAME(this_name)):  this_name=this_user.upper()

    DICT2CSV(LOGIN_XL_PATH, 
             { f'{this_user}' : [DEFAULT_ACCESS,  f'{this_user}', f'{this_name}', f''] }, 
             LOGIN_ORD ) # save updated login information to csv
    
    sprint(f'⇒ Created new login-db with admin-user: user-id "{this_user}" and name "{this_name}"')

# ------------------------------------------------------------------------------------------
# EVAL DATABASE - CSV
# ------------------------------------------------------------------------------------------
if not args.eval: EVAL_XL_PATH = None # fexit(f'[!] evaluation file was not provided!')    
else: EVAL_XL_PATH = os.path.join( BASEDIR, args.eval)
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# download settings
# ------------------------------------------------------------------------------------------
if not args.downloads: fexit(f'[!] downloads folder was not provided!')
DOWNLOAD_FOLDER_PATH = os.path.join( BASEDIR, args.downloads) 
try: os.makedirs(DOWNLOAD_FOLDER_PATH, exist_ok=True)
except: fexit(f'[!] downloads folder @ {DOWNLOAD_FOLDER_PATH} was not found and could not be created')
sprint(f'⚙ Download Folder: {DOWNLOAD_FOLDER_PATH}') 
# ------------------------------------------------------------------------------------------
# store settings
# ------------------------------------------------------------------------------------------
if not args.store: fexit(f'[!] store folder was not provided!')
STORE_FOLDER_PATH = os.path.join( BASEDIR, args.store) 
try: os.makedirs(STORE_FOLDER_PATH, exist_ok=True)
except: fexit(f'[!] store folder @ {STORE_FOLDER_PATH} was not found and could not be created')
sprint(f'⚙ Store Folder: {STORE_FOLDER_PATH}')
# ------------------------------------------------------------------------------------------
# upload settings
# ------------------------------------------------------------------------------------------
if not args.uploads: fexit(f'[!] uploads folder was not provided!')
UPLOAD_FOLDER_PATH = os.path.join( BASEDIR, args.uploads ) 
try: os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)
except: fexit(f'[!] uploads folder @ {UPLOAD_FOLDER_PATH} was not found and could not be created')
sprint(f'⚙ Upload Folder: {UPLOAD_FOLDER_PATH}')
# ------------------------------------------------------------------------------------------
# report settings
# ------------------------------------------------------------------------------------------
if not args.reports: fexit(f'[!] reports folder was not provided!')
REPORT_FOLDER_PATH = os.path.join( BASEDIR, args.reports ) 
try: os.makedirs(REPORT_FOLDER_PATH, exist_ok=True)
except: fexit(f'[!] reports folder @ {REPORT_FOLDER_PATH} was not found and could not be created')
sprint(f'⚙ Reports Folder: {REPORT_FOLDER_PATH}')

#-----------------------------------------------------------------------------------------
# file-name and uploads validation
#-----------------------------------------------------------------------------------------
ALLOWED_EXTENSIONS = set([x.strip() for x in args.ext.split(',') if x])  # a set or list of file extensions that are allowed to be uploaded 
if '' in ALLOWED_EXTENSIONS: ALLOWED_EXTENSIONS.remove('')
VALID_FILES_PATTERN = r'^[\w\-. ]+\.(?:' + '|'.join(ALLOWED_EXTENSIONS) + r')$'
REQUIRED_FILES = set([x.strip() for x in args.required.split(',') if x])  # a set or list of file extensions that are required to be uploaded 
if '' in REQUIRED_FILES: REQUIRED_FILES.remove('')
def VALIDATE_FILENAME(instr):           return rematch(instr, r'^[a-zA-Z]+(?: [a-zA-Z]+)*$')
def VALIDATE_FILENAME_SUBMIT(instr):     return rematch(instr, r'^[a-zA-Z]+(?: [a-zA-Z]+)*$')
def VALIDATE_FILENAME(filename):   # a function that checks for valid file extensions based on ALLOWED_EXTENSIONS
    if '.' in filename: 
        name, ext = filename.rsplit('.', 1)
        safename = f'{name}.{ext.lower()}'
        if REQUIRED_FILES:  isvalid = (safename in REQUIRED_FILES)
        else:               isvalid = re.match(VALID_FILES_PATTERN, safename, re.IGNORECASE)  # Case-insensitive matching
    else:               
        name, ext = filename, ''
        safename = f'{name}'
        if REQUIRED_FILES:  isvalid = (safename in REQUIRED_FILES)
        else:               isvalid = (not ALLOWED_EXTENSIONS)
    return isvalid, safename

VALID_FILE_EXT_SUBMIT = ['csv', 'txt']
VALID_FILES_PATTERN_SUMBIT = r'^[\w\-. ]+\.(?:' + '|'.join(VALID_FILE_EXT_SUBMIT) + r')$'
def VALIDATE_FILENAME_SUBMIT(filename): 
    if '.' in filename: 
        name, ext = filename.rsplit('.', 1)
        safename = f'{name}.{ext.lower()}'
        isvalid = isvalid = re.match(VALID_FILES_PATTERN_SUMBIT, safename, re.IGNORECASE)
    else:               
        name, ext = filename, ''
        safename = f'{name}'
        isvalid = False
    return isvalid, safename

def str2bytes(size):
    sizes = dict(KB=2**10, MB=2**20, GB=2**30, TB=2**40)
    return int(float(size[:-2])*sizes.get(size[-2:].upper(), 0))
MAX_UPLOAD_SIZE = str2bytes(args.maxupsize)     # maximum upload file size 
MAX_UPLOAD_COUNT = ( inf if args.maxupcount<0 else args.maxupcount )       # maximum number of files that can be uploaded by one user
INITIAL_UPLOAD_STATUS = []           # a list of notes to be displayed to the users about uploading files
if REQUIRED_FILES: INITIAL_UPLOAD_STATUS.append((-1, f'accepted files [{len(REQUIRED_FILES)}]: {REQUIRED_FILES}'))
else:
    if ALLOWED_EXTENSIONS:  INITIAL_UPLOAD_STATUS.append((-1, f'allowed extensions [{len(ALLOWED_EXTENSIONS)}]: {ALLOWED_EXTENSIONS}'))
INITIAL_UPLOAD_STATUS.append((-1, f'max upload size: {DISPLAY_SIZE_READABLE(MAX_UPLOAD_SIZE)}'))
if not (MAX_UPLOAD_COUNT is inf): INITIAL_UPLOAD_STATUS.append((-1, f'max upload count: {MAX_UPLOAD_COUNT}'))
sprint(f'⚙ Upload Settings ({len(INITIAL_UPLOAD_STATUS)})')
for s in INITIAL_UPLOAD_STATUS: sprint(f' ⇒ {s[1]}')
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# html pages
# ------------------------------------------------------------------------------------------
style = Fake(**args.style)
from . import TEMPLATES
HTML_TEMPLATES, CSS_TEMPLATES = TEMPLATES(style)
# ------------------------------------------------------------------------------------------
for k,v in HTML_TEMPLATES.items():
    h = os.path.join(HTMLDIR, f"{k}.html")
    if (not os.path.isfile(h)) or bool(parsed.cos):
        try:
            with open(h, 'w', encoding='utf-8') as f: f.write(v)
        except: fexit(f'[!] Cannot create html "{k}" at {h}')
# ------------------------------------------------------------------------------------------
for k,v in CSS_TEMPLATES.items():
    h = os.path.join(HTMLDIR, f"{k}.css")
    if (not os.path.isfile(h)) or bool(parsed.cos):
        try:
            with open(h, 'w', encoding='utf-8') as f: f.write(v)
        except: fexit(f'[!] Cannot create css "{k}" at {h}')
# ------------------------------------------------------------------------------------------
sprint(f'↪ Created html/css templates @ {HTMLDIR}')
# ------------------------------------------------------------------------------------------
favicon_path = os.path.join(HTMLDIR, f"favicon.ico")
if not os.path.exists(favicon_path):
    try: 
        from . import FAVICON
        FAVICON(favicon_path)
        del FAVICON
    except: pass
# ------------------------------------------------------------------------------------------
# delete pages dict after creation? #- keep the keys to "coe"
HTML_TEMPLATES_KEYS = tuple(HTML_TEMPLATES.keys()) #{k:None for k in HTML_TEMPLATES} 
CSS_TEMPLATES_KEYS = tuple(CSS_TEMPLATES.keys()) #{k:None for k in CSS_TEMPLATES}
del TEMPLATES, HTML_TEMPLATES, CSS_TEMPLATES_KEYS
# ------------------------------------------------------------------------------------------
# Board
# ------------------------------------------------------------------------------------------
BOARD_FILE_MD = None
BOARD_PAGE = ""
if args.board:
    if has_nbconvert_package:
        BOARD_FILE_MD = os.path.join(BASEDIR, f'{args.board}')
        if  os.path.isfile(BOARD_FILE_MD): sprint(f'⚙ Board File: {BOARD_FILE_MD}')
        else: 
            sprint(f'⚙ Board File: {BOARD_FILE_MD} not found - trying to create...')
            try:
                with open(BOARD_FILE_MD, 'w', encoding='utf-8') as f: f.write(NEW_NOTEBOOK_STR(f'# {args.topic}'))
                sprint(f'⚙ Board File: {BOARD_FILE_MD} was created successfully!')
            except:
                BOARD_FILE_MD = None
                sprint(f'⚙ Board File: {BOARD_FILE_MD} could not be created - Board will not be available!')
    else: sprint(f'[!] Board will not be enabled since it requires nbconvert')
if not BOARD_FILE_MD:   sprint(f'⚙ Board: Not Available')
else: sprint(f'⚙ Board: Is Available')
# ------------------------------------------------------------------------------------------
def update_board(): 
    global BOARD_PAGE
    res = False
    if BOARD_FILE_MD:
        try: 
            page,_ = HTMLExporter(template_name=style.template_board).from_file(BOARD_FILE_MD, {'metadata':{'name':f'{style.icon_board} {style.board_} | {args.topic}'}}) 
            BOARD_PAGE = page
            sprint(f'⚙ Board File was updated: {BOARD_FILE_MD}')
            res=True
        except: 
            BOARD_PAGE=""
            sprint(f'⚙ Board File could not be updated: {BOARD_FILE_MD}')
    else: BOARD_PAGE=""
    return res

_ = update_board()
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# Database Read/Write
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
def read_logindb_from_disk():
    db_frame, res = READ_DB_FROM_DISK(LOGIN_XL_PATH, 1)
    if res: sprint(f'⇒ Loaded login file: {LOGIN_XL_PATH}')
    else: sprint(f'⇒ Failed reading login file: {LOGIN_XL_PATH}')
    return db_frame
def read_evaldb_from_disk():
    dbsub_frame = dict()
    if EVAL_XL_PATH: 
        dbsub_frame, ressub = READ_DB_FROM_DISK(EVAL_XL_PATH, 0)
        if ressub: sprint(f'⇒ Loaded evaluation file: {EVAL_XL_PATH}')
        else: sprint(f'⇒ Did not load evaluation file: [{EVAL_XL_PATH}] exists={os.path.exists(EVAL_XL_PATH)} isfile={os.path.isfile(EVAL_XL_PATH)}')
    return dbsub_frame
# ------------------------------------------------------------------------------------------
def write_logindb_to_disk(db_frame): # will change the order
    res = WRITE_DB_TO_DISK(LOGIN_XL_PATH, db_frame, LOGIN_ORD)
    if res: sprint(f'⇒ Persisted login file: {LOGIN_XL_PATH}')
    else:  sprint(f'⇒ PermissionError - {LOGIN_XL_PATH} might be open, close it first.')
    return res
def write_evaldb_to_disk(dbsub_frame, verbose=True): # will change the order
    ressub = True
    if EVAL_XL_PATH: 
        ressub = WRITE_DB_TO_DISK(EVAL_XL_PATH, dbsub_frame, EVAL_ORD)
        if verbose:
            if ressub: sprint(f'⇒ Persisted evaluation file: {EVAL_XL_PATH}')
            else:  sprint(f'⇒ PermissionError - {EVAL_XL_PATH} might be open, close it first.')
    return ressub
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
db =    read_logindb_from_disk()  #<----------- Created database here 
dbsub = read_evaldb_from_disk()  #<----------- Created database here 
sprint('↷ persisted eval-db [{}]'.format(write_evaldb_to_disk(dbsub)))
dbevalset = set([k for k,v in db.items() if '-' not in v[0]])
# ------------------------------------------------------------------------------------------
# Check user upload requirements
# ------------------------------------------------------------------------------------------
def GetUserFiles(uid): 
    if not REQUIRED_FILES: return True # no files are required to be uploaded
    udir = os.path.join( app.config['uploads'], uid)
    has_udir = os.path.isdir(udir)
    if has_udir: return not (False in [os.path.isfile(os.path.join(udir, f)) for f in REQUIRED_FILES])
    else: return False
class UploadFileForm(FlaskForm): # The upload form using FlaskForm
    file = MultipleFileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
# ------------------------------------------------------------------------------------------
# application setting and instance
# ------------------------------------------------------------------------------------------
LOGIN_REG_TEXT =        '👤'
LOGIN_NEED_TEXT =       '🔒'
LOGIN_FAIL_TEXT =       '❌'     
LOGIN_NEW_TEXT =        '🔥'
LOGIN_CREATE_TEXT =     '🔑'    
#%% [APP DEFINE] @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 
app = Flask(
    __name__,
    static_folder=HTMLDIR,      # Set your custom static folder path here
    template_folder=HTMLDIR,   # Set your custom templates folder path here
    instance_relative_config = True,
    instance_path = WORKDIR,
)
# ------------------------------------------------------------------------------------------
# app config
# ------------------------------------------------------------------------------------------
app.secret_key =          APP_SECRET_KEY
app.config['base'] =      BASEDIR
app.config['uploads'] =   UPLOAD_FOLDER_PATH
app.config['reports'] =   REPORT_FOLDER_PATH
app.config['downloads'] = DOWNLOAD_FOLDER_PATH
app.config['store'] =     STORE_FOLDER_PATH
app.config['storename'] =  os.path.basename(STORE_FOLDER_PATH)
app.config['storeuser'] =     UPLOAD_FOLDER_PATH
app.config['storeusername'] =  os.path.basename(UPLOAD_FOLDER_PATH)
app.config['emoji'] =     args.emoji
app.config['topic'] =     args.topic
app.config['dfl'] =       GET_FILE_LIST(DOWNLOAD_FOLDER_PATH)
app.config['rename'] =    int(args.rename)
app.config['muc'] =       MAX_UPLOAD_COUNT
app.config['board'] =     (BOARD_FILE_MD is not None)
app.config['reg'] =       (parsed.reg)
app.config['repass'] =    bool(args.repass)
app.config['eip'] =       bool(parsed.eip)
app.config['apac'] =    f'{parsed.access}'.strip().upper()
# ------------------------------------------------------------------------------------------



#%% [ROUTES] @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 
# ------------------------------------------------------------------------------------------
# login
# ------------------------------------------------------------------------------------------
@app.route('/', methods =['GET', 'POST'])
def route_login():
    if request.method == 'POST' and 'uid' in request.form and 'passwd' in request.form:
        global db
        in_uid = f"{request.form['uid']}"
        in_passwd = f"{request.form['passwd']}"
        in_name = f'{request.form["named"]}' if 'named' in request.form else ''
        in_emoji = app.config['emoji']
        in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
        valid_query, valid_name = VALIDATE_UID(in_query) , VALIDATE_NAME(in_name)
        if not valid_query : record=None
        else: record = db.get(in_query, None)
        if record is not None: 
            admind, uid, named, passwd = record
            if not passwd: # fist login
                if in_passwd: # new password provided
                    if VALIDATE_PASS(in_passwd): # new password is valid
                        db[uid][3]=in_passwd 
                        if in_name!=named and valid_name and (app.config['rename']>0) : 
                            db[uid][2]=in_name
                            dprint(f'⇒ {uid} ◦ {named} updated name to "{in_name}" via {request.remote_addr}') 
                            named = in_name
                        else:
                            if in_name: dprint(f'⇒ {uid} ◦ {named} provided invalid name "{in_name}" (will not update)') 

                        warn = LOGIN_CREATE_TEXT
                        msg = f'[{in_uid}] ({named}) New password was created successfully'
                        dprint(f'● {in_uid} {in_emoji} {named} just joined via {request.remote_addr}')
           
                    else: # new password is invalid valid 
                        warn = LOGIN_NEW_TEXT
                        msg=f'[{in_uid}] New password is invalid - can use any of the alphabets (A-Z, a-z), numbers (0-9), underscore (_), dot (.) and at-symbol (@) only'
                        
                                               
                else: #new password not provided                
                    warn = LOGIN_NEW_TEXT
                    msg = f'[{in_uid}] New password required - can use any of the alphabets (A-Z, a-z), numbers (0-9), underscore (_), dot (.) and at-symbol (@) only'
                                           
            else: # re login
                if in_passwd: # password provided 
                    if in_passwd==passwd:
                        folder_name = os.path.join(app.config['uploads'], uid)
                        folder_report = os.path.join(app.config['reports'], uid) 
                        try:
                            os.makedirs(folder_name, exist_ok=True)
                            os.makedirs(folder_report, exist_ok=True)
                        except:
                            dprint(f'✗ directory could not be created @ {folder_name} :: Force logout user {uid}')
                            session['has_login'] = False
                            session['uid'] = uid
                            session['named'] = named
                            session['emojid'] = ''
                            return redirect(url_for('route_logout'))
                    
                        session['has_login'] = True
                        session['uid'] = uid
                        session['admind'] = admind + app.config['apac']
                        session['filed'] = os.listdir(folder_name)
                        session['reported'] = sorted(os.listdir(folder_report))
                        session['emojid'] = in_emoji 
                        session['hidden_store'] = False
                        session['hidden_storeuser'] = True
                        
                        if in_name!=named and  valid_name and  (app.config['rename']>0): 
                            session['named'] = in_name
                            db[uid][2] = in_name
                            dprint(f'⇒ {uid} ◦ {named} updated name to "{in_name}" via {request.remote_addr}') 
                            named = in_name
                        else: 
                            session['named'] = named
                            if in_name: dprint(f'⇒ {uid} ◦ {named} provided invalid name "{in_name}" (will not update)')  

                        dprint(f'● {session["uid"]} {session["emojid"]} {session["named"]} has logged in via {request.remote_addr}') 
                        return redirect(url_for('route_home'))
                    else:  
                        warn = LOGIN_FAIL_TEXT
                        msg = f'[{in_uid}] Password mismatch'                  
                else: # password not provided
                    warn = LOGIN_FAIL_TEXT
                    msg = f'[{in_uid}] Password not provided'
        else:
            warn = LOGIN_FAIL_TEXT
            msg = f'[{in_uid}] Not a valid user' 

    else:
        if session.get('has_login', False):  return redirect(url_for('route_home'))
        msg = args.welcome
        warn = LOGIN_NEED_TEXT 
        
    return render_template('login.html', msg = msg,  warn = warn)
# ------------------------------------------------------------------------------------------
# new
# ------------------------------------------------------------------------------------------
@app.route('/new', methods =['GET', 'POST'])
def route_new():
    if not app.config['reg']: return "registration is not allowed"
    if request.method == 'POST' and 'uid' in request.form and 'passwd' in request.form:
        global db
        in_uid = f"{request.form['uid']}"
        in_passwd = f"{request.form['passwd']}"
        in_name = f'{request.form["named"]}' if 'named' in request.form else ''
        in_emoji = app.config['emoji']
        in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
        valid_query, valid_name = VALIDATE_UID(in_query) , VALIDATE_NAME(in_name)
        if not valid_query:
            warn, msg = LOGIN_FAIL_TEXT, f'[{in_uid}] Not a valid user-id' 
        elif not valid_name:
            warn, msg = LOGIN_FAIL_TEXT, f'[{in_name}] Not a valid name' 
        else:
            record = db.get(in_query, None)
            if record is None: 
                if not app.config['reg']:
                    warn, msg = LOGIN_FAIL_TEXT, f'[{in_uid}] not allowed to register' 
                else:
                    admind, uid, named = app.config['reg'], in_query, in_name
                    if in_passwd: # new password provided
                        if VALIDATE_PASS(in_passwd): # new password is valid
                            db[uid] = [admind, uid, named, in_passwd]
                            warn = LOGIN_CREATE_TEXT
                            msg = f'[{in_uid}] ({named}) New password was created successfully'
                            dprint(f'● {in_uid} {in_emoji} {named} just joined via {request.remote_addr}')
            
                        else: # new password is invalid valid  
                            warn = LOGIN_NEW_TEXT
                            msg=f'[{in_uid}] New password is invalid - can use any of the alphabets (A-Z, a-z), numbers (0-9), underscore (_), dot (.) and at-symbol (@) only'
                            
                                                
                    else: #new password not provided                  
                        warn = LOGIN_NEW_TEXT
                        msg = f'[{in_uid}] New password required - can use any of the alphabets (A-Z, a-z), numbers (0-9), underscore (_), dot (.) and at-symbol (@) only'
                                            

            else:
                warn, msg = LOGIN_FAIL_TEXT, f'[{in_uid}] is already registered' 

    else:
        if session.get('has_login', False):  return redirect(url_for('route_home'))
        msg = args.register
        warn = LOGIN_REG_TEXT 
        
    return render_template('new.html', msg = msg,  warn = warn)
# ------------------------------------------------------------------------------------------
# logout
# ------------------------------------------------------------------------------------------
@app.route('/logout')
def route_logout():
    r""" logout a user and redirect to login page """
    if not session.get('has_login', False):  return redirect(url_for('route_login'))
    if not session.get('uid', False): return redirect(url_for('route_login'))
    if session['has_login']:  dprint(f'● {session["uid"]} {session["emojid"]} {session["named"]} has logged out via {request.remote_addr}') 
    else: dprint(f'✗ {session["uid"]} ◦ {session["named"]} was removed due to invalid uid ({session["uid"]}) via {request.remote_addr}') 
    session.clear()
    return redirect(url_for('route_login'))
# ------------------------------------------------------------------------------------------
# board
# ------------------------------------------------------------------------------------------
@app.route('/board', methods =['GET'])
def route_board():
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if 'B' not in session['admind']:  return redirect(url_for('route_home'))
    if '?' in (request.args) and '+' in session['admind']: 
        if update_board(): 
            dprint(f"▶ {session['uid']} ◦ {session['named']} just refreshed the board via {request.remote_addr}")
            return redirect(url_for('route_board'))
    return BOARD_PAGE
# ------------------------------------------------------------------------------------------
# download
# ------------------------------------------------------------------------------------------
@app.route('/downloads', methods =['GET'], defaults={'req_path': ''})
@app.route('/downloads/<path:req_path>')
def route_downloads(req_path):
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if 'D' not in session['admind']:  return redirect(url_for('route_home'))
    abs_path = os.path.join(app.config['downloads'], req_path) # Joining the base and the requested path
    if not req_path:
        if '?' in request.args and '+' in session['admind']: 
            app.config['dfl'] = GET_FILE_LIST(DOWNLOAD_FOLDER_PATH)
            dprint(f"▶ {session['uid']} ◦ {session['named']} just refreshed the download list via {request.remote_addr}")
            return redirect(url_for('route_downloads'))
    else:
        if not os.path.exists(abs_path): 
            dprint(f"⇒ requested file was not found {abs_path}") #Return 404 if path doesn't exist
            return abort(404) # (f"◦ requested file was not found") #Return 404 if path doesn't exist
        if os.path.isfile(abs_path):  #(f"◦ sending file ")
            dprint(f'● {session["uid"]} ◦ {session["named"]} just downloaded the file {req_path} via {request.remote_addr}')
            return send_file(abs_path) # Check if path is a file and serve
    return render_template('downloads.html')
# ------------------------------------------------------------------------------------------
# uploads
# ------------------------------------------------------------------------------------------
@app.route('/uploads', methods =['GET'], defaults={'req_path': ''})
@app.route('/uploads/<path:req_path>')
def route_uploads(req_path):
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if 'S' not in session['admind']:  return redirect(url_for('route_home'))
    abs_path = os.path.join(os.path.join( app.config['uploads'], session['uid']) , req_path)# Joining the base and the requested path
    if not os.path.exists(abs_path): 
        dprint(f"⇒ requested file was not found {abs_path}") #Return 404 if path doesn't exist
        return abort(404) # (f"◦ requested file was not found") #Return 404 if path doesn't exist
    if os.path.isfile(abs_path):  #(f"◦ sending file ")
        dprint(f'● {session["uid"]} ◦ {session["named"]} just downloaded the file {req_path} via {request.remote_addr}')
        return send_file(abs_path) # Check if path is a file and serve
    return render_template('uploads.html')
# ------------------------------------------------------------------------------------------
# reports
# ------------------------------------------------------------------------------------------
@app.route('/reports', methods =['GET'], defaults={'req_path': ''})
@app.route('/reports/<path:req_path>')
def route_reports(req_path):
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if 'R' not in session['admind']:  return redirect(url_for('route_home'))
    abs_path = os.path.join(os.path.join( app.config['reports'], session['uid']) , req_path)# Joining the base and the requested path
    if not os.path.exists(abs_path): 
        dprint(f"⇒ requested file was not found {abs_path}") #Return 404 if path doesn't exist
        return abort(404) # (f"◦ requested file was not found") #Return 404 if path doesn't exist
    if os.path.isfile(abs_path):  #(f"◦ sending file ")
        dprint(f'● {session["uid"]} ◦ {session["named"]} just downloaded the report {req_path} via {request.remote_addr}')
        return send_file(abs_path) # Check if path is a file and serve
    return render_template('reports.html')
# ------------------------------------------------------------------------------------------
@app.route('/generate_eval_template', methods =['GET'])
def route_generate_eval_template():
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if not (('X' in session['admind']) or ('+' in session['admind'])): return abort(404)
    return send_file(DICT2BUFF({k:[v[LOGIN_ORD_MAPPING["UID"]], v[LOGIN_ORD_MAPPING["NAME"]], "", "",] for k,v in db.items() if '-' not in v[LOGIN_ORD_MAPPING["ADMIN"]]} , ["UID", "NAME", "SCORE", "REMARKS"]),
                    download_name=f"eval_{app.config['topic']}_{session['uid']}.csv", as_attachment=True)
@app.route('/generate_submit_report', methods =['GET'])
def route_generate_submit_report():
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if not (('X' in session['admind']) or ('+' in session['admind'])): return abort(404)
    finished_uids = set(dbsub.keys())
    remaining_uids = dbevalset.difference(finished_uids)
    absent_uids = set([puid for puid in remaining_uids if not os.path.isdir(os.path.join( app.config['uploads'], puid))])
    pending_uids = remaining_uids.difference(absent_uids)
    msg = f"Total [{len(dbevalset)}]"
    if len(dbevalset) != len(finished_uids) + len(pending_uids) + len(absent_uids): msg+=f" [!] Count Mismatch!"
    pending_uids, absent_uids, finished_uids = sorted(list(pending_uids)), sorted(list(absent_uids)), sorted(list(finished_uids))
    return \
    f"""
    <style>
    td {{padding: 10px;}}
    th {{padding: 5px;}}
    tr {{vertical-align: top;}}
    </style>
    <h3> {msg} </h3>
    <table border="1">
        <tr>
            <th>Pending [{len(pending_uids)}]</th>
            <th>Absent [{len(absent_uids)}]</th>
            <th>Finished [{len(finished_uids)}]</th>
        </tr>
        <tr>
            <td><pre>{NEWLINE.join(pending_uids)}</pre></td>
            <td><pre>{NEWLINE.join(absent_uids)}</pre></td>
            <td><pre>{NEWLINE.join(finished_uids)}</pre></td>
        </tr>
        
    </table>
    """
# ------------------------------------------------------------------------------------------
# eval
# ------------------------------------------------------------------------------------------
@app.route('/eval', methods =['GET', 'POST'])
def route_eval():
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    form = UploadFileForm()
    submitter = session['uid']
    results = []
    if form.validate_on_submit():
        dprint(f"● {session['uid']} ◦ {session['named']} is trying to upload {len(form.file.data)} items via {request.remote_addr}")
        if  not ('X' in session['admind']): status, success =  "You are not allow to evaluate.", False
        else: 
            if not EVAL_XL_PATH: status, success =  "Evaluation is disabled.", False
            else:
                if len(form.file.data)!=1:  status, success = f"Expecting only one csv file", False
                else:
                    #---------------------------------------------------------------------------------
                    file = form.file.data[0]
                    isvalid, sf = VALIDATE_FILENAME_SUBMIT(secure_filename(file.filename))
                    #---------------------------------------------------------------------------------
                    if not isvalid: status, success = f"Extension is invalid '{sf}' - Accepted extensions are {VALID_FILE_EXT_SUBMIT}", False
                    else:
                        try: 
                            filebuffer = BytesIO()
                            file.save(filebuffer) 
                            score_dict = BUFF2DICT(filebuffer, 0)
                            results.clear()
                            for k,v in score_dict.items():
                                in_uid = v[0] #f"{request.form['uid']}"
                                in_score = v[2] #f"{request.form['score']}"
                                in_remark = v[3]
                                if not (in_score or in_remark): continue
                                if in_score:
                                    try: _ = float(in_score)
                                    except: in_score=''
                                in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
                                valid_query = VALIDATE_UID(in_query) 
                                if not valid_query : 
                                    results.append((in_uid,f'[{in_uid}] is not a valid user.', False))
                                else: 
                                    record = db.get(in_query, None)
                                    if record is None: 
                                        results.append((in_uid,f'[{in_uid}] is not a valid user.', False))
                                    else:
                                        admind, uid, named, _ = record
                                        if ('-' in admind):
                                            results.append((in_uid,f'[{in_uid}] {named} is not in evaluation list.', False))
                                        else:
                                            scored = dbsub.get(in_query, None)                               
                                            if scored is None: # not found
                                                if not in_score:
                                                    results.append((in_uid,f'Require numeric value to assign score to [{in_uid}] {named}.', False))
                                                else:
                                                    has_req_files = GetUserFiles(uid)
                                                    if has_req_files:
                                                        dbsub[in_query] = [uid, named, in_score, in_remark, submitter]
                                                        results.append((in_uid,f'Score/Remark Created for [{in_uid}] {named}, current score is {in_score}.', True))
                                                        dprint(f"▶ {submitter} ◦ {session['named']} just evaluated {uid} ◦ {named} via {request.remote_addr}")
                                                    else:
                                                        results.append((in_uid,f'User [{in_uid}] {named} has not uploaded the required files yet.', False))
                                            else:
                                                if scored[-1] == submitter or abs(float(scored[2])) == float('inf') or ('+' in session['admind']):
                                                    if in_score:  dbsub[in_query][2] = in_score
                                                    if in_remark: dbsub[in_query][3] = in_remark
                                                    dbsub[in_query][-1] = submitter # incase of inf score
                                                    if in_score or in_remark : results.append((in_uid,f'Score/Remark Updated for [{in_uid}] {named}, current score is {dbsub[in_query][2]}. Remark is [{dbsub[in_query][3]}].', True))
                                                    else: results.append((in_uid,f'Nothing was updated for [{in_uid}] {named}, current score is {dbsub[in_query][2]}. Remark is [{dbsub[in_query][3]}].', False))
                                                    dprint(f"▶ {submitter} ◦ {session['named']} updated the evaluation for {uid} ◦ {named} via {request.remote_addr}")
                                                else:
                                                    results.append((in_uid,f'[{in_uid}] {named} has been evaluated by [{scored[-1]}], you cannot update the information. Hint: Set the score to "inf".', False))
                                                    dprint(f"▶ {submitter} ◦ {session['named']} is trying to revaluate {uid} ◦ {named} (already evaluated by [{scored[-1]}]) via {request.remote_addr}")
                            vsu = [vv for nn,kk,vv in results]
                            vsuc = vsu.count(True)
                            success = (vsuc > 0)
                            status = f'Updated {vsuc} of {len(vsu)} records'
                        except: 
                            status, success = f"Error updating scroes from file [{sf}]", False
        if success: persist_subdb()
    elif request.method == 'POST': 
        if 'uid' in request.form and 'score' in request.form:
            if EVAL_XL_PATH:
                if ('X' in session['admind']) or ('+' in session['admind']):
                    in_uid = f"{request.form['uid']}"
                    in_score = f"{request.form['score']}"
                    if in_score:
                        try: _ = float(in_score)
                        except: in_score=''
                    in_remark = f'{request.form["remark"]}' if 'remark' in request.form else ''
                    in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
                    valid_query = VALIDATE_UID(in_query) 
                    if not valid_query : 
                        status, success = f'[{in_uid}] is not a valid user.', False
                    else: 
                        record = db.get(in_query, None)
                        if record is None: 
                            status, success = f'[{in_uid}] is not a valid user.', False
                        else:
                            admind, uid, named, _ = record
                            if ('-' in admind):
                                status, success = f'[{in_uid}] {named} is not in evaluation list.', False
                            else:
                                scored = dbsub.get(in_query, None)                               
                                if scored is None: # not found
                                    if not in_score:
                                        status, success = f'Require numeric value to assign score to [{in_uid}] {named}.', False
                                    else:
                                        has_req_files = GetUserFiles(uid)
                                        if has_req_files:
                                            dbsub[in_query] = [uid, named, in_score, in_remark, submitter]
                                            status, success = f'Score/Remark Created for [{in_uid}] {named}, current score is {in_score}.', True
                                            dprint(f"▶ {submitter} ◦ {session['named']} just evaluated {uid} ◦ {named} via {request.remote_addr}")
                                        else:
                                            status, success = f'User [{in_uid}] {named} has not uploaded the required files yet.', False
                                else:
                                    if scored[-1] == submitter or abs(float(scored[2])) == float('inf') or ('+' in session['admind']):
                                        if in_score:  dbsub[in_query][2] = in_score
                                        if in_remark: dbsub[in_query][3] = in_remark
                                        dbsub[in_query][-1] = submitter # incase of inf score
                                        if in_score or in_remark : status, success =    f'Score/Remark Updated for [{in_uid}] {named}, current score is {dbsub[in_query][2]}. Remark is [{dbsub[in_query][3]}].', True
                                        else: status, success =                         f'Nothing was updated for [{in_uid}] {named}, current score is {dbsub[in_query][2]}. Remark is [{dbsub[in_query][3]}].', False
                                        dprint(f"▶ {submitter} ◦ {session['named']} updated the evaluation for {uid} ◦ {named} via {request.remote_addr}")
                                    else:
                                        status, success = f'[{in_uid}] {named} has been evaluated by [{scored[-1]}], you cannot update the information. Hint: Set the score to "inf".', False
                                        dprint(f"▶ {submitter} ◦ {session['named']} is trying to revaluate {uid} ◦ {named} (already evaluated by [{scored[-1]}]) via {request.remote_addr}")
                else: status, success =  "You are not allow to evaluate.", False
            else: status, success =  "Evaluation is disabled.", False
        else: status, success = f"You posted nothing!", False
        if success and app.config['eip']: persist_subdb()
    else:
        if ('+' in session['admind']) or ('X' in session['admind']):
            status, success = f"Eval Access is Enabled", True
        else: status, success = f"Eval Access is Disabled", False
    return render_template('evaluate.html', success=success, status=status, form=form, results=results)
# ------------------------------------------------------------------------------------------
# home - upload
# ------------------------------------------------------------------------------------------
@app.route('/home', methods =['GET', 'POST'])
def route_home():
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    form = UploadFileForm()
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    if EVAL_XL_PATH:
        submitted = int(session['uid'] in dbsub)
        score = dbsub[session['uid']][2] if submitted>0 else -1
    else: submitted, score = -1, -1

    if form.validate_on_submit() and ('U' in session['admind']):
        dprint(f"● {session['uid']} ◦ {session['named']} is trying to upload {len(form.file.data)} items via {request.remote_addr}")
        if app.config['muc']==0: 
            return render_template('home.html', submitted=submitted, score=score, form=form, status=[(0, f'✗ Uploads are disabled')])
        
        if EVAL_XL_PATH:
            if submitted>0: return render_template('home.html', submitted=submitted, score=score, form=form, status=[(0, f'✗ You have been evaluated - cannot upload new files for this session.')])

        result = []
        n_success = 0
        #---------------------------------------------------------------------------------
        for file in form.file.data:
            isvalid, sf = VALIDATE_FILENAME(secure_filename(file.filename))
            isvalid = isvalid or ('+' in session['admind'])
        #---------------------------------------------------------------------------------
            
            if not isvalid:
                why_failed =  f"✗ File not accepted [{sf}] " if REQUIRED_FILES else f"✗ Extension is invalid [{sf}] "
                result.append((0, why_failed))
                continue

            file_name = os.path.join(folder_name, sf)
            if not os.path.exists(file_name):
                if len(session['filed'])>=app.config['muc']:
                    why_failed = f"✗ Upload limit reached [{sf}] "
                    result.append((0, why_failed))
                    continue
            
            try: 
                file.save(file_name) 
                why_failed = f"✓ Uploaded new file [{sf}] "
                result.append((1, why_failed))
                n_success+=1
                if sf not in session['filed']: session['filed'] = session['filed'] + [sf]
            except FileNotFoundError: 
                return redirect(url_for('route_logout'))


            

        #---------------------------------------------------------------------------------
            
        result_show = ''.join([f'\t{r[-1]}\n' for r in result])
        result_show = result_show[:-1]
        dprint(f'✓ {session["uid"]} ◦ {session["named"]} just uploaded {n_success} file(s)\n{result_show}') 
        return render_template('home.html', submitted=submitted, score=score, form=form, status=result)
    
    return render_template('home.html', submitted=submitted, score=score, form=form, status=(INITIAL_UPLOAD_STATUS if app.config['muc']!=0 else [(-1, f'Uploads are disabled')]))
# ------------------------------------------------------------------------------------------
@app.route('/uploadf', methods =['GET'])
def route_uploadf():
    r""" force upload - i.e., refresh by using os.list dir """
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    session['filed'] = os.listdir(folder_name)
    folder_report = os.path.join(app.config['reports'], session['uid']) 
    session['reported'] = sorted(os.listdir(folder_report))
    return redirect(url_for('route_home'))
# ------------------------------------------------------------------------------------------
# purge
# ------------------------------------------------------------------------------------------
@app.route('/purge', methods =['GET'])
def route_purge():
    r""" purges all files that a user has uploaded in their respective uplaod directory
    NOTE: each user will have its won directory, so choose usernames such that a corresponding folder name is a valid one
    """
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if 'U' not in session['admind']:  return redirect(url_for('route_home'))
    if EVAL_XL_PATH:
        #global dbsub
        if session['uid'] in dbsub: return redirect(url_for('route_home'))

    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    if os.path.exists(folder_name):
        file_list = os.listdir(folder_name)
        for f in file_list: os.remove(os.path.join(folder_name, f))
        dprint(f'● {session["uid"]} ◦ {session["named"]} used purge via {request.remote_addr}')
        session['filed']=[]
    return redirect(url_for('route_home'))
# ------------------------------------------------------------------------------------------

class HConv: # html converter
   
    @staticmethod
    def convert(abs_path):
        new_abs_path = f'{abs_path}.html'
        if abs_path.lower().endswith(".ipynb"):
            try:
                x = __class__.nb2html( abs_path )
                with open(new_abs_path, 'w') as f: f.write(x)
                return True, (f"rendered Notebook to HTML @ {new_abs_path}")
            except: return False, (f"failed to rendered Notebook to HTML @ {new_abs_path}") 
        else: return False, (f"no renderer exists for {abs_path}")

    @staticmethod
    def remove_tag(page, tag): # does not work on nested tags
        fstart, fstop = f'<{tag}', f'/{tag}>'
        while True:
            istart = page.find(fstart)
            if istart<0: break
            istop = page[istart:].find(fstop)
            page = f'{page[:istart]}{page[istart+istop+len(fstop):]}'
        return page
    
    @staticmethod
    def nb2html(source_notebook, template_name='lab', no_script=True, html_title=None, parsed_title='Notebook',):
        #if not has_nbconvert_package: return f'<div>Requires nbconvert: python -m pip install nbconvert</div>'
        if html_title is None: # auto infer
            html_title = os.path.basename(source_notebook)
            iht = html_title.rfind('.')
            if not iht<0: html_title = html_title[:iht]
            if not html_title: html_title = (parsed_title if parsed_title else os.path.basename(os.path.dirname(source_notebook)))
        try:    
            page, _ = HTMLExporter(template_name=template_name).from_file(source_notebook,  dict(  metadata = dict( name = f'{html_title}' )    )) 
            if no_script: page = __class__.remove_tag(page, 'script') # force removing any scripts
        except: page = None
        return  page

# ------------------------------------------------------------------------------------------
# store
# ------------------------------------------------------------------------------------------
def list_store_dir(abs_path):
    dirs, files = [], []
    with os.scandir(abs_path) as it:
        for item in it:
            if item.is_file(): files.append((item.name, item.name.startswith(".")))
            elif item.is_dir(): dirs.append((item.name, item.name.startswith(".")))
            else: pass
    return dirs, files
# ------------------------------------------------------------------------------------------
@app.route('/hidden_show/<path:user_enable>', methods =['GET'])
def route_hidden_show(user_enable=''):
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if len(user_enable)!=2:  return redirect(url_for('route_home'))
    if user_enable[0]=='0':
        session['hidden_store'] = (user_enable[1]!='0')
        return redirect(url_for('route_store'))
    else:
        session['hidden_storeuser'] = (user_enable[1]!='0')
        return redirect(url_for('route_storeuser'))
# ------------------------------------------------------------------------------------------
@app.route('/store', methods =['GET'])
@app.route('/store/', methods =['GET'])
@app.route('/store/<path:subpath>', methods =['GET'])
def route_store(subpath=""):
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if ('A' not in session['admind']) :  return abort(404)
    abs_path = os.path.join(app.config['store'], subpath)
    if not os.path.exists(abs_path): return abort(404)
        
    if os.path.isdir(abs_path):
        dirs, files = list_store_dir(abs_path)
        return render_template('store.html', dirs=dirs, files=files, subpath=subpath, )
    elif os.path.isfile(abs_path): 
        dprint(f"● {session['uid']} ◦ {session['named']}  downloaded {abs_path} via {request.remote_addr}")
        return send_file(abs_path, as_attachment=("get" in request.args))
    else: return abort(404)
# ------------------------------------------------------------------------------------------
@app.route('/storeuser', methods =['GET'])
@app.route('/storeuser/', methods =['GET'])
@app.route('/storeuser/<path:subpath>', methods =['GET'])
def route_storeuser(subpath=""):
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if ('X' not in session['admind']):  return abort(404)
    abs_path = os.path.join(app.config['storeuser'], subpath)
    if not os.path.exists(abs_path): return abort(404)
        
    if os.path.isdir(abs_path):
        dirs, files = list_store_dir(abs_path)
        return render_template('storeuser.html', dirs=dirs, files=files, subpath=subpath, )
    elif os.path.isfile(abs_path): 
        
        if ("html" in request.args): 
            dprint(f"● {session['uid']} ◦ {session['named']} converting to html from {subpath} via {request.remote_addr}")
            if has_nbconvert_package: hstatus, hmsg = HConv.convert(abs_path)
            else: hstatus, hmsg = False, f"missing package - nbconvert"
            
            dprint(f"{TABLINE}{'... ✓' if hstatus else '... ✗'} {hmsg}")
            return redirect(url_for('route_storeuser', subpath=os.path.dirname(subpath))) 
        else: 
            dprint(f"● {session['uid']} ◦ {session['named']} downloaded {subpath} from user-store via {request.remote_addr}")
            return send_file(abs_path, as_attachment=("get" in request.args))
    else: return abort(404)
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# administrative and password reset
# ------------------------------------------------------------------------------------------

def persist_db():
    r""" writes both dbs to disk """
    global db, dbsub
    if write_logindb_to_disk(db) and write_evaldb_to_disk(dbsub): #if write_db_to_disk(db, dbsub):
        dprint(f"▶ {session['uid']} ◦ {session['named']} just persisted the db to disk via {request.remote_addr}")
        STATUS, SUCCESS = "Persisted db to disk", True
    else: STATUS, SUCCESS =  f"Write error, file might be open", False
    return STATUS, SUCCESS 

def persist_subdb():
    r""" writes eval-db to disk """
    global dbsub
    if write_evaldb_to_disk(dbsub, verbose=False): STATUS, SUCCESS = "Persisted db to disk", True
    else: STATUS, SUCCESS =  f"Write error, file might be open", False
    return STATUS, SUCCESS 

def reload_db():
    r""" reloads db from disk """
    global db, dbsub
    db = read_logindb_from_disk()
    dbsub = read_evaldb_from_disk()
    dprint(f"▶ {session['uid']} ◦ {session['named']} just reloaded the db from disk via {request.remote_addr}")
    return "Reloaded db from disk", True #  STATUS, SUCCESS

@app.route('/x/', methods =['GET'], defaults={'req_uid': ''})
@app.route('/x/<req_uid>')
def route_repassx(req_uid):
    r""" reset user password"""
    if not session.get('has_login', False): return redirect(url_for('route_login')) # "Not Allowed - Requires Login"
    form = UploadFileForm()
    results = []
    if not req_uid:
        if '+' in session['admind']: 
            if len(request.args)==1:
                if '?' in request.args: STATUS, SUCCESS = reload_db()
                elif '!' in request.args: STATUS, SUCCESS = persist_db()
                else: STATUS, SUCCESS =  f'Invalid command ({next(iter(request.args.keys()))}) ... Hint: use (?) (!) ', False
            else: 
                if len(request.args)>1: STATUS, SUCCESS =  f"Only one command is accepted ... Hint: use (?) (!) ", False
                else: STATUS, SUCCESS =  f"Admin Access is Enabled", True
        else:  STATUS, SUCCESS =  f"Admin Access is Disabled", False
    else:
        iseval, isadmin = ('X' in session['admind']), ('+' in session['admind'])
        global db
        if request.args:  
            if isadmin:
                try: 
                    in_uid = f'{req_uid}'
                    if in_uid: 
                        in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
                        valid_query = VALIDATE_UID(in_query)
                        if not valid_query: STATUS, SUCCESS = f'[{in_uid}] Not a valid user-id' , False
                        else:
                            named = request.args.get('name', "")
                            admind = request.args.get('access', "")
                            record = db.get(in_query, None)
                            if record is None: 
                                if named and admind:
                                    valid_name = VALIDATE_NAME(named)
                                    if not valid_name: STATUS, SUCCESS = f'[{named}] Requires a valid name' , False
                                    else:
                                        db[in_query] = [admind, in_query, named, '']
                                        dprint(f"▶ {session['uid']} ◦ {session['named']} just added a new user {in_query} ◦ {named} via {request.remote_addr}")
                                        STATUS, SUCCESS =  f"New User Created {in_query} {named}", True
                                else: STATUS, SUCCESS = f'Missing Arguments to create new user "{in_query}": use (name) (access)' , False
                            else:
                                STATUS, SUCCESS =  f"Updated Nothing for {in_query}", False
                                radmind, _, rnamed, _ = record
                                if admind and admind!=radmind: # trying to update access
                                    db[in_query][0] = admind
                                    dprint(f"▶ {session['uid']} ◦ {session['named']} just updated access for {in_query} from {radmind} to {admind} via {request.remote_addr}")
                                    STATUS, SUCCESS =  f"Updated Access for {in_query} from [{radmind}] to [{admind}]", True

                                if named and named!=rnamed: # trying to rename
                                    valid_name = VALIDATE_NAME(named)
                                    if not valid_name: 
                                        STATUS, SUCCESS = f'[{named}] Requires a valid name' , False
                                    else:
                                        db[in_query][2] = named
                                        dprint(f"▶ {session['uid']} ◦ {session['named']} just updated name for {in_query} from {rnamed} to {named} via {request.remote_addr}")
                                        STATUS, SUCCESS =  f"Updated Name for {in_query} from [{rnamed}] to [{named}]", True
                                
                                
                                #STATUS, SUCCESS =  f"User '{in_query}' already exists", False


                    else: STATUS, SUCCESS =  f"User-id was not provided", False
                except: STATUS, SUCCESS = f'Invalid request args ... Hint: use (name, access)'
            else: STATUS, SUCCESS =  f"Admin Access is Disabled", False
        else:
            if app.config['repass']:
                
                if iseval or isadmin:
                    in_uid = f'{req_uid}'
                    if in_uid: 
                        in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
                        record = db.get(in_query, None)
                        if record is not None: 
                            admind, uid, named, _ = record
                            if (('X' not in admind) and ('+' not in admind)) or isadmin or (session['uid']==uid):
                                db[uid][3]='' ## 3 for PASS
                                dprint(f"▶ {session['uid']} ◦ {session['named']} just reset the password for {uid} ◦ {named} via {request.remote_addr}")
                                STATUS, SUCCESS =  f"Password was reset for {uid} {named}", True
                            else: STATUS, SUCCESS =  f"You cannot reset password for account '{in_query}'", False
                        else: STATUS, SUCCESS =  f"User '{in_query}' not found", False
                    else: STATUS, SUCCESS =  f"User-id was not provided", False
                else: STATUS, SUCCESS =  "You are not allow to reset passwords", False
            else: STATUS, SUCCESS =  "Password reset is disabled for this session", False
        
    return render_template('evaluate.html',  status=STATUS, success=SUCCESS, form=form, results=results)
# ------------------------------------------------------------------------------------------

#%% [READY TO SERVE]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# DO NOT WRITE ANY NEW CODE AFTER THIS
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#%% [SERVER] @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def endpoints(athost):
    if athost=='0.0.0.0':
        ips=set()
        try:
            import socket
            for info in socket.getaddrinfo(socket.gethostname(), None):
                if (info[0].name == socket.AddressFamily.AF_INET.name): ips.add(info[4][0])
        except: pass
        ips=list(ips)
        ips.extend(['127.0.0.1', 'localhost'])
        return ips
    else: return [f'{athost}']

start_time = datetime.datetime.now()
sprint('◉ start server @ [{}]'.format(start_time))
for endpoint in endpoints(args.host): sprint(f'◉ http://{endpoint}:{args.port}')
serve(app, # https://docs.pylonsproject.org/projects/waitress/en/stable/runner.html
    host = args.host,          
    port = args.port,          
    url_scheme = 'http',     
    threads = args.threads,    
    connection_limit = args.maxconnect,
    max_request_body_size = MAX_UPLOAD_SIZE,
)
end_time = datetime.datetime.now()
sprint('◉ stop server @ [{}]'.format(end_time))
sprint('↷ persisted login-db [{}]'.format(write_logindb_to_disk(db)))
sprint('↷ persisted eval-db [{}]'.format(write_evaldb_to_disk(dbsub)))

if bool(parsed.coe):
    sprint(f'↪ Cleaning up html/css templates...')
    try:
        for k in HTML_TEMPLATES_KEYS:#.items():
            h = os.path.join(HTMLDIR, f"{k}.html")
            if  os.path.isfile(h) : os.remove(h)
        #sprint(f'↪ Removing css templates @ {STATIC_DIR}')
        for k in CSS_TEMPLATES_KEYS:#.items():
            h = os.path.join(HTMLDIR, f"{k}.css")
            if os.path.isfile(h): os.remove(h)
        #os.removedirs(TEMPLATES_DIR)
        #os.removedirs(STATIC_DIR)
        sprint(f'↪ Removed html/css templates @ {HTMLDIR}')
    except:
        sprint(f'↪ Could not remove html/css templates @ {HTMLDIR}')
sprint('◉ server up-time was [{}]'.format(end_time - start_time))
sprint(f'...Finished!')
#%% [END]
# ✓
# ✗
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# author: Nelson.S
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
