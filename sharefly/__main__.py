__doc__=f""" 
-------------------------------------------------------------
ShareFly - Flask-based web app for sharing files 
-------------------------------------------------------------
DEFAULT_ACCESS:
D   Read from Downloads
A   Read from Store
B   Access Board
U   Perform Upload
S   Read from Self Uploads
R   Read from Reports
+   Admin access enabled
X   Reset access enabled (password reset)
-   Not included in evaluation
"""
# ✗ ✓

#-----------------------------------------------------------------------------------------
from sys import exit
if __name__!='__main__': exit(f'[!] can not import {__name__}.{__file__}')
#-----------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
LOGDIR = f'{parsed.log}' # define log dir - contains all logs
LOGFILE = None
if LOGDIR and parsed.verbose>0: 

    LOGFILENAME = f'{fnow(parsed.logname)}'
    if not LOGFILENAME: exit(f'[!] Provided logfile nameLogging directory was not found and could not be created is blank!')

    try: os.makedirs(LOGDIR, exist_ok=True)
    except: exit(f'[!] Logging directory was not found and could not be created')
# ------------------------------------------------------------------------------------------
    try:
        # Set up logging to a file
        LOGFILE = os.path.join(LOGDIR, LOGFILENAME)
        logging.basicConfig(filename=LOGFILE, level=logging.INFO, format='%(asctime)s - %(message)s')
        # also output to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(console_handler)
    except: exit(f'[!] Logging could not be setup at {LOGFILE}')
# ------------------------------------------------------------------------------------------


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


sprint(f'Starting...')
sprint(f'↪ Logging @ {LOGFILE}')

# ------------------------------------------------------------------------------------------
WORKDIR = f'{parsed.dir}' # define working dir - contains all bases
if not WORKDIR: WORKDIR = os.getcwd()
WORKDIR=os.path.abspath(WORKDIR)
try: os.makedirs(WORKDIR, exist_ok=True)
except: fexit(f'[!] Workspace directory was not found and could not be created')
sprint(f'↪ Workspace directory is {WORKDIR}')


#-----------------------------------------------------------------------------------------
# ==> read configurations
#-----------------------------------------------------------------------------------------
CONFIG = parsed.con if parsed.con else 'default' # the config-dict to read from
CONFIG_MODULE = '__configs__'  # the name of configs module
CONFIGS_FILE = f'{CONFIG_MODULE}.py' # the name of configs file

CSV_DELIM = ','
SSV_DELIM = '\n'
MAX_STR_LEN = int(parsed.msl) if parsed.msl>0 else 1
NEWLINE = '\n'
TABLINE = '\t'

LOGIN_ORD = ['ADMIN','UID','NAME','PASS']
LOGIN_ORD_MAPPING = {v:i for i,v in enumerate(LOGIN_ORD)}
EVAL_ORD = ['UID', 'NAME', 'SCORE', 'REMARK', 'BY']

DEFAULT_USER = 'admin'
DEFAULT_ACCESS = f'DABUSRX+-'


#-----------------------------------------------------------------------------------------

def rematch(instr, pattern):  return \
    (len(instr) >= 0) and \
    (len(instr) <= MAX_STR_LEN) and \
    (re.match(pattern, instr))

def VALIDATE_PASS(instr):     return rematch(instr, r'^[a-zA-Z0-9~!@#$%^&*()_+{}<>?`\-=\[\].]+$')
def VALIDATE_UID(instr):      return rematch(instr, r'^[a-zA-Z0-9._@]+$')
def VALIDATE_NAME(instr):     return rematch(instr, r'^[a-zA-Z]+(?: [a-zA-Z]+)*$')

# this is useful for docker
# we try to read args from os env variables
def DEFAULT_CONFIG_GENERATE(): return """

def merged(a:dict, b:dict): return {**a, **b}

default = dict(    

    # -------------------------------------# general info
    topic        = "ShareFly",             # topic text (main banner text)
    welcome      = "Welcome!",             # msg shown on login page
    register     = "Register!",            # msg shown on register (new-user) page
    emoji        = "🦋",                   # emoji shown of login page and seperates uid - name
    rename       = 0,                      # if rename=1, allows users to update their names when logging in
    repass       = 1,                      # if repass=1, allows admins and Xs to reset passwords for users - should be enabled in only one session (for multi-session)
    case         = 0,                      # case-sentivity level in uid
                                            #   (if case=0 uids are not converted           when matching in database)
                                            #   (if case>0 uids are converted to upper-case when matching in database)
                                            #   (if case<0 uids are converted to lower-case when matching in database)
    
    # -------------------------------------# validation
    ext          = "",                     # csv list of file-extensions that are allowed to be uploaded e.g., ext = "jpg,jpeg,png,txt" (keep blank to allow all extensions)
    required     = "",                     # csv list of file-names that are required to be uploaded e.g., required = "a.pdf,b.png,c.exe" (keep blank to allow all file-names)
    maxupcount   = -1,                     # maximum number of files that can be uploaded by a user (keep -1 for no limit and 0 to disable uploading)
    maxupsize    = "40GB",                 # maximum size of uploaded file (html_body_size)
    
    # -------------------------------------# server config
    maxconnect   = 50,                     # maximum number of connections allowed to the server
    threads      = 4,                      # no. of threads used by waitress server
    port         = "8888",                 # port
    host         = "0.0.0.0",              # ip

    # ------------------------------------# file and directory information
    base 		 = "__base__",            # the base directory 
    html         = "__pycache__",         # use pycache dir to store flask html
    secret       = "__secret__.txt",      # flask app secret
    login        = "__login__.csv",       # login database
    eval         = "__eval__.csv",        # evaluation database - created if not existing - reloads if exists
    uploads      = "__uploads__",         # uploads folder (uploaded files by users go here)
    reports      = "__reports__",         # reports folder (personal user access files by users go here)
    downloads    = "__downloads__",       # downloads folder
    store        = "__store__",           # store folder
    board        = "__board__.ipynb",     # board file
    # --------------------------------------# style dict
    style        = dict(                   
                        # -------------# labels
                        downloads_ =    'Downloads',
                        uploads_ =      'Uploads',
                        store_ =        'Store',
                        board_=         'Board',
                        admin_=         'Admin',
                        logout_=        'Logout',
                        login_=         'Login',
                        new_=           'Register',
                        eval_=          'Eval',
                        resetpass_=     'Reset',
                        report_=        'Report',

                        # -------------# colors 
                        bgcolor      = "white",                 # background
                        fgcolor      = "black",                 # foreground
                        refcolor     = "teal",                  # link 
                        item_bgcolor = "#232323",
                        item_normal  = "white",
                        item_true    = "#47ff6f",
                        item_false   = "#ff6565",
                        flup_bgcolor = "#ebebeb",
                        flup_fgcolor = "#232323",
                        fldown_bgcolor = "#ebebeb",
                        fldown_fgcolor = "#232323",
                        msgcolor =     "#060472",
                        
                        # -------------# icons 
                        icon_board =    '🔰',
                        icon_admin=     '⭐',
                        icon_login=     '🔒',
                        icon_new=       '👤',
                        icon_home=      '🔘',
                        icon_downloads= '📥',
                        icon_uploads=   '📤',
                        icon_store=     '📦',
                        icon_eval=      '✴️',
                        icon_report=    '📜',
                        icon_getfile=   '⬇️',
                        icon_gethtml=   '🌐',

                        # -------------# admin actions 
                        aa_ref_downloads =  '📥',
                        aa_db_write=     	'💾',
                        aa_db_read=       	'👁️‍🗨️',
                        aa_ref_board=      	'🔰',
                        aa_reset_pass= 		'🔑',

                        # -------------# board style ('lab'  'classic' 'reveal')
                        template_board = 'lab', 
                    )
    )

""" 


def DEFAULT_CONFIG_WRITE(file_path):
    with open(file_path, 'w', encoding='utf-8') as f: f.write(DEFAULT_CONFIG_GENERATE())



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

APPEND_ACCESS = f'{parsed.access}'.strip().upper()


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
    for _ in range(datetime.datetime.now().second): _ = randx()
    r2 = randx()
    for _ in range(datetime.datetime.now().second): _ = randx()
    r3 = randx()
    for _ in range(datetime.datetime.now().second): _ = randx()
    r4 = randx()
    return ':{}:{}:{}:{}:{}:'.format(r1,r2,r3,r4,postfix)


def CREATE_LOGIN_FILE(login_xl_path):  
    this_user = getpass.getuser()
    if not (VALIDATE_UID(this_user)):  this_user=DEFAULT_USER
    DICT2CSV(login_xl_path, { f'{this_user}' : [DEFAULT_ACCESS,  f'{this_user}', f'{this_user}', f''] }, LOGIN_ORD ) # save updated login information to csv
    return this_user


def READ_DB_FROM_DISK(path, key_at):
    try:    return CSV2DICT(path, key_at), True
    except: return dict(), False
# ------------------------------------------------------------------------------------------
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


#-----------------------------------------------------------------------------------------
# Special Objects
#-----------------------------------------------------------------------------------------
class Fake:
    def __len__(self): return len(self.__dict__)
    def __init__(self, **kwargs) -> None:
        for name, attribute in kwargs.items():  setattr(self, name, attribute)
#-----------------------------------------------------------------------------------------


# try to import configs
CONFIGS_FILE_PATH = os.path.join(WORKDIR, CONFIGS_FILE) # should exsist under workdir
if not os.path.isfile(CONFIGS_FILE_PATH):
    sprint(f'↪ Creating default config "{CONFIGS_FILE}" ...')
    DEFAULT_CONFIG_WRITE(CONFIGS_FILE_PATH)
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
# ******************************************************************************************


HTMLDIR = ((os.path.join(WORKDIR, args.html)) if args.html else WORKDIR)
try: os.makedirs(HTMLDIR, exist_ok=True)
except: fexit(f'[!] HTML directory was not found and could not be created')
sprint(f'⚙ HTML Directory @ {HTMLDIR}')

    
# Read base dir first 
BASEDIR = ((os.path.join(WORKDIR, args.base)) if args.base else WORKDIR)
try:     os.makedirs(BASEDIR, exist_ok=True)
except:  fexit(f'[!] base directory  @ {BASEDIR} was not found and could not be created') 
sprint(f'⚙ Base dicectiry: {BASEDIR}')
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
    this_user = CREATE_LOGIN_FILE(LOGIN_XL_PATH)
    sprint(f'⇒ Created new login with user "{this_user}" at file: {LOGIN_XL_PATH}')

# ------------------------------------------------------------------------------------------

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


ALLOWED_EXTENSIONS = set([x.strip() for x in args.ext.split(',') if x])  # a set or list of file extensions that are allowed to be uploaded 
if '' in ALLOWED_EXTENSIONS: ALLOWED_EXTENSIONS.remove('')
VALID_FILES_PATTERN = pattern = r'^[\w\-. ]+\.(?:' + '|'.join(ALLOWED_EXTENSIONS) + r')$'
REQUIRED_FILES = set([x.strip() for x in args.required.split(',') if x])  # a set or list of file extensions that are required to be uploaded 
if '' in REQUIRED_FILES: REQUIRED_FILES.remove('')
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
VALID_FILES_PATTERN_SUMBIT = pattern = r'^[\w\-. ]+\.(?:' + '|'.join(VALID_FILE_EXT_SUBMIT) + r')$'
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
#-----------------------------------------------------------------------------------------
# Create HTML
# ------------------------------------------------------------------------------------------
style = Fake(**args.style)

# ******************************************************************************************
HTML_TEMPLATES = dict(
# ******************************************************************************************
board="""""",
# ******************************************************************************************
evaluate = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_eval}'+""" {{ config.topic }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">  
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <div class="bridge">
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{style.logout_}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_home">Home</a>
        <a href="{{ url_for('route_eval') }}" class="btn_refresh">Refresh</a>
        <a href="{{ url_for('route_storeuser') }}" class="btn_store">User-Store</a>
        <a href="{{ url_for('route_generate_submit_report') }}" target="_blank" class="btn_board">User-Report</a>
        <button class="btn_purge_large" onclick="confirm_repass()">"""+f'{style.aa_reset_pass} Reset Password' + """</button>
            <script>
                function confirm_repass() {
                let res = prompt("Enter UID", ""); 
                if (res != null) {
                    location.href = "{{ url_for('route_repassx',req_uid='::::') }}".replace("::::", res);
                    }
                }
            </script>
        </div>
        <br>
        {% if success %}
        <span class="admin_mid" style="animation-name: fader_admin_success;">✓ {{ status }} </span>
        {% else %}
        <span class="admin_mid" style="animation-name: fader_admin_failed;">✗ {{ status }} </span>
        {% endif %}
        <br>
        <br>
        <form action="{{ url_for('route_eval') }}" method="post">
            
                <input id="uid" name="uid" type="text" placeholder="uid" class="txt_submit"/>
                <br>
                <br>
                <input id="score" name="score" type="text" placeholder="score" class="txt_submit"/> 
                <br>
                <br>
                <input id="remark" name="remark" type="text" placeholder="remarks" class="txt_submit"/>
                <br>
                <br>
                <input type="submit" class="btn_submit" value="Submit Evaluation"> 
                <br>   
                <br> 
        </form>
        
        <form method='POST' enctype='multipart/form-data'>
            {{form.hidden_tag()}}
            {{form.file()}}
            {{form.submit()}}
        </form>
        <a href="{{ url_for('route_generate_eval_template') }}" class="btn_admin">Get CSV-Template</a>
        <br>
     
    </div>
    
    {% if results %}
    <div class="status">
    <table>
    {% for (ruid,rmsg,rstatus) in results %}
        {% if rstatus %}
            <tr class="btn_disablel">
        {% else %}
            <tr class="btn_enablel">
        {% endif %}
            <td>{{ ruid }} ~ </td>
            <td>{{ rmsg }}</td>
            </tr>
    {% endfor %}
    </table>
    </div>
    {% endif %}
                
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",

# ******************************************************************************************
admin = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_admin}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
					 
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <div class="bridge">
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{style.logout_}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_home">Home</a>
        <a href="{{ url_for('route_adminpage') }}" class="btn_refresh">Refresh</a>
        </div>
        <br>
        {% if success %}
        <span class="admin_mid" style="animation-name: fader_admin_success;">✓ {{ status }} </span>
        {% else %}
        <span class="admin_mid" style="animation-name: fader_admin_failed;">✗ {{ status }} </span>
        {% endif %}
        <br>
        {% if '+' in session.admind %}
        <a href="{{ url_for('route_adminpage',req_cmd='ref_downloads') }}" class="btn_admin_actions">"""+f'{style.aa_ref_downloads}'+"""<span class="tooltiptext">Refresh Downloads</span></a> <!--Update download-list --!>
        <a href="{{ url_for('route_adminpage',req_cmd='db_write') }}" class="btn_admin_actions">"""+f'{style.aa_db_write}'+"""<span class="tooltiptext">Persist Database</span></a> <!--Persist login-database --!>
        <a href="{{ url_for('route_adminpage',req_cmd='db_read') }}" class="btn_admin_actions">"""+f'{style.aa_db_read}'+"""<span class="tooltiptext">Reload Database</span></a> <!--Reload login-database --!>
        <a href="{{ url_for('route_adminpage',req_cmd='ref_board') }}" class="btn_admin_actions">"""+f'{style.aa_ref_board}'+"""<span class="tooltiptext">Refresh Board</span></a> <!--Refresh board --!>
        <button class="btn_admin_actions" onclick="confirm_repass()">"""+f'{style.aa_reset_pass}'+"""<span class="tooltiptext">Reset Password</span></button>
        
            <script>
                function confirm_repass() {
                let res = prompt("Enter UID", ""); 
                if (res != null) {
                    location.href = "{{ url_for('route_repass',req_uid='::::') }}".replace("::::", res);
                    }
                }
            </script>
        {% endif %}
    </div>
            
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
login = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_login}'+""" {{ config.topic }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">  
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">

    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->

    <div align="center">
        <br>
        <div class="topic">{{ config.topic }}</div>
        <br>
        <br>
        <form action="{{ url_for('route_login') }}" method="post">
            <br>
            <div style="font-size: x-large;">{{ warn }}</div>
            <br>
            <div class="msg_login">{{ msg }}</div>
            <br>
            <input id="uid" name="uid" type="text" placeholder="... user-id ..." class="txt_login"/>
            <br>
            <br>
            <input id="passwd" name="passwd" type="password" placeholder="... password ..." class="txt_login"/>
            <br>
            <br>
            {% if config.rename>0 %}
            <input id="named" name="named" type="text" placeholder="... update-name ..." class="txt_login"/>
            {% if config.rename>1 %}
            <input id="emojid" name="emojid" type="text" placeholder={{ config.emoji }} class="txt_login_small"/>
            {% endif %}
            <br>
            {% endif %}
            <br>
            <input type="submit" class="btn_login" value=""" +f'"{style.login_}"'+ """> 
            <br>
            <br>
        </form>
    </div>

    <!-- ---------------------------------------------------------->
    
    <div align="center">
    <div>
    <a href="https://github.com/NelsonSharma/sharefly" target="_blank"><span style="font-size: xx-large;">{{ config.emoji }}</span></a>
    <br>
    {% if config.reg %}
    <a href="{{ url_for('route_new') }}" class="btn_board">""" + f'{style.new_}' +"""</a>
    {% endif %}
    </div>
    <br>
    </div>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
new = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_new}'+""" {{ config.topic }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">  
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">

    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->

    <div align="center">
        <br>
        <div class="topic">{{ config.topic }}</div>
        <br>
        <br>
        <form action="{{ url_for('route_new') }}" method="post">
            <br>
            <div style="font-size: x-large;">{{ warn }}</div>
            <br>
            <div class="msg_login">{{ msg }}</div>
            <br>
            <input id="uid" name="uid" type="text" placeholder="... user-id ..." class="txt_login"/>
            <br>
            <br>
            <input id="passwd" name="passwd" type="password" placeholder="... password ..." class="txt_login"/>
            <br>
            <br>
            <input id="named" name="named" type="text" placeholder="... name ..." class="txt_login"/>
            <br>
            <br>
            <input type="submit" class="btn_board" value=""" + f'"{style.new_}"' +"""> 
            <br>
            <br>
            
        </form>
    </div>

    <!-- ---------------------------------------------------------->
    
    <div align="center">
    <div>
    <span style="font-size: xx-large;">{{ config.emoji }}</span>
    <br>
    <a href="{{ url_for('route_login') }}" class="btn_login">""" + f'{style.login_}' +"""</a>
    
    </div>
    <br>
    </div>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
downloads = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_downloads}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">           
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">

    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <div class="bridge">
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{style.logout_}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_home">Home</a>
        </div>
        <br>
        <div class="files_status">"""+f'{style.downloads_}'+"""</div>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in config.dfl %}
            <li><a href="{{ (request.path + '/' if request.path != '/' else '') + file }}"" >{{ file }}</a></li>
            <br>
            {% endfor %}
            </ol>
        </div>
        <br>
    </div>

    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
storeuser = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_store}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">   
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
        
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <div class="bridge">
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{style.logout_}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_home">Home</a>
        <a href="{{ url_for('route_eval') }}" class="btn_submit">"""+f'{style.eval_}'+"""</a>
        {% if not subpath %}
        {% if session.hidden_storeuser %}
            <span class="files_status">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Hidden Files: </span><a href="{{ url_for('route_hidden_show', user_enable='10') }}" class="btn_disable">Enabled</a>
        {% else %}
            <span class="files_status">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Hidden Files: </span><a href="{{ url_for('route_hidden_show', user_enable='11') }}" class="btn_enable">Disabled</a>
        {% endif %}
        {% endif %}
        </div>
        <br>
        <hr>
        <!-- Breadcrumb for navigation -->
        <div class="files_status"> Path: 
            {% if subpath %}
                <a href="{{ url_for('route_storeuser') }}" class="btn_store">{{ config.storeusername }}</a>{% for part in subpath.split('/') %}🔹<a href="{{ url_for('route_storeuser', subpath='/'.join(subpath.split('/')[:loop.index])) }}" class="btn_store">{{ part }}</a>{% endfor %}  
            {% else %}
                <a href="{{ url_for('route_storeuser') }}" class="btn_store">{{ config.storeusername }}</a>
            {% endif %}
        </div>
        <hr>
        <!-- Directory Listing -->
        
        <div class="files_list_up">
            <p class="files_status">Folders</p>
            {% for (dir,hdir) in dirs %}
                {% if (session.hidden_storeuser) or (not hdir) %}
                    <a href="{{ url_for('route_storeuser', subpath=subpath + '/' + dir) }}" class="btn_folder">{{ dir }}</a>
                {% endif %}
            {% endfor %}
        </div>
        <hr>
        
        <div class="files_list_down">
            <p class="files_status">Files</p>
            <ol>
            {% for (file, hfile) in files %}
            {% if (session.hidden_storeuser) or (not hfile) %}
                <li>
                <a href="{{ url_for('route_storeuser', subpath=subpath + '/' + file, get='') }}">"""+f'{style.icon_getfile}'+"""</a> 
                <a href="{{ url_for('route_storeuser', subpath=subpath + '/' + file) }}" target="_blank">{{ file }}</a>
                {% if file.lower().endswith('.ipynb') %}
                <a href="{{ url_for('route_storeuser', subpath=subpath + '/' + file, html='') }}">"""+f'{style.icon_gethtml}'+"""</a> 
                {% endif %}
                </li>
            {% endif %}
            
            {% endfor %}
            </ol>
        </div>
        <br>
    </div>

    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
store = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_store}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">      
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
     
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <div class="bridge">
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{style.logout_}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_home">Home</a>
        {% if not subpath %}
        {% if session.hidden_store %}
            <span class="files_status">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Hidden Files: </span><a href="{{ url_for('route_hidden_show', user_enable='00') }}" class="btn_disable">Enabled</a>
        {% else %}
            <span class="files_status">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Hidden Files: </span><a href="{{ url_for('route_hidden_show', user_enable='01') }}" class="btn_enable">Disabled</a>
        {% endif %}
        {% endif %}
        </div>
        <br>
        <hr>
        <!-- Breadcrumb for navigation -->
        <div class="files_status"> Path: 
            {% if subpath %}
                <a href="{{ url_for('route_store') }}" class="btn_store">{{ config.storename }}</a>{% for part in subpath.split('/') %}🔹<a href="{{ url_for('route_store', subpath='/'.join(subpath.split('/')[:loop.index])) }}" class="btn_store">{{ part }}</a>{% endfor %}  
            {% else %}
                <a href="{{ url_for('route_store') }}" class="btn_store">{{ config.storename }}</a>
            {% endif %}
        </div>
        <hr>
        <!-- Directory Listing -->
        
        <div class="files_list_up">
            <p class="files_status">Folders</p>
            {% for (dir,hdir) in dirs %}
                {% if (session.hidden_store) or (not hdir) %}
                    <a href="{{ url_for('route_store', subpath=subpath + '/' + dir) }}" class="btn_folder">{{ dir }}</a>
                {% endif %}
            {% endfor %}
        </div>
        <hr>
        
        <div class="files_list_down">
            <p class="files_status">Files</p>
            <ol>
            {% for (file, hfile) in files %}
            {% if (session.hidden_store) or (not hfile) %}
                <li>
                <a href="{{ url_for('route_store', subpath=subpath + '/' + file, get='') }}">"""+f'{style.icon_getfile}'+"""</a> 
                <a href="{{ url_for('route_store', subpath=subpath + '/' + file) }}" target="_blank" >{{ file }}</a>
               
                </li>
            {% endif %}
            
            {% endfor %}
            </ol>
        </div>
        <br>
    </div>

    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
uploads = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_uploads}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">        
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
   
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <div class="bridge">
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{style.logout_}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_home">Home</a>
        </div>
        <br>
        <div class="files_status">"""+f'{style.uploads_}'+"""</div>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in session.filed %}
            <li><a href="{{ (request.path + '/' if request.path != '/' else '') + file }}">{{ file }}</a></li>
            <br>
            {% endfor %}
            </ol>
        </div>
        <br>
    </div>

    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
reports = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_report}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">     
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
      
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <div class="bridge">
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{style.logout_}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_home">Home</a>
        </div>
        <br>
        <div class="files_status">"""+f'{style.report_}'+"""</div>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in session.reported %}
            <li><a href="{{ (request.path + '/' if request.path != '/' else '') + file }}"  target="_blank">{{ file }}</a></li>
            <br>
            {% endfor %}
            </ol>
        </div>
        <br>
    </div>

    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
home="""
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{style.icon_home}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">			
        <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
		 
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <div class="bridge">
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{style.logout_}'+"""</a>
        {% if "S" in session.admind %}
        <a href="{{ url_for('route_uploads') }}" class="btn_upload">"""+f'{style.uploads_}'+"""</a>
        {% endif %}
        {% if "D" in session.admind %}
        <a href="{{ url_for('route_downloads') }}" class="btn_download">"""+f'{style.downloads_}'+"""</a>
        {% endif %}
        {% if "A" in session.admind %}
        <a href="{{ url_for('route_store') }}" class="btn_store">"""+f'{style.store_}'+"""</a>
        {% endif %}
        {% if "B" in session.admind and config.board %}
        <a href="{{ url_for('route_board') }}" class="btn_board" target="_blank">"""+f'{style.board_}'+"""</a>
        {% endif %}
        {% if 'X' in session.admind or '+' in session.admind %}
        <a href="{{ url_for('route_eval') }}" class="btn_submit">"""+f'{style.eval_}'+"""</a>
        {% endif %}
        {% if 'R' in session.admind %}
        <a href="{{ url_for('route_reports') }}" class="btn_report">"""+f'{style.report_}'+"""</a>
        {% endif %}
        
        {% if '+' in session.admind %}
        <a href="{{ url_for('route_adminpage') }}" class="btn_admin">"""+f'{style.admin_}'+"""</a>
        {% endif %}
        </div>
        <br>
        {% if "U" in session.admind %}
            <div class="status">
                <ol>
                {% for s,f in status %}
                {% if s %}
                {% if s<0 %}
                <li style="color: """+f'{style.item_normal}'+""";">{{ f }}</li>
                {% else %}
                <li style="color: """+f'{style.item_true}'+""";">{{ f }}</li>
                {% endif %}
                {% else %}
                <li style="color: """+f'{style.item_false}'+""";">{{ f }}</li>
                {% endif %}
                {% endfor %}
                </ol>
            </div>
            <br>
            {% if submitted<1 %}
                {% if config.muc!=0 %}
                <form method='POST' enctype='multipart/form-data'>
                    {{form.hidden_tag()}}
                    {{form.file()}}
                    {{form.submit()}}
                </form>
                {% endif %}
            {% else %}
                <div class="upword">Your Score is <span style="color:seagreen;">{{ score }}</span>  </div>
            {% endif %}
            <br>
                
            <div> <span class="upword">Uploads</span> 
                
            {% if submitted<1 and config.muc!=0 %}
                <a href="{{ url_for('route_uploadf') }}" class="btn_refresh_small">Refresh</a>
                <button class="btn_purge" onclick="confirm_purge()">Purge</button>
                <script>
                    function confirm_purge() {
                    let res = confirm("Purge all the uploaded files now?");
                    if (res == true) {
                        location.href = "{{ url_for('route_purge') }}";
                        }
                    }
                </script>
            {% endif %}
            </div>
            <br>

            <div class="files_list_up">
                <ol>
                {% for f in session.filed %}
                    <li>{{ f }}</li>
                {% endfor %}
                </ol>
            </div>
        {% endif %}
        
            
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
#******************************************************************************************

# ******************************************************************************************
)
# ******************************************************************************************
CSS_TEMPLATES = dict(
# ****************************************************************************************** 0b7daa
style = f""" 

body {{
    background-color: {style.bgcolor};
    color: {style.fgcolor};
}}

a {{
    color: {style.refcolor};
    text-decoration: none;
}}

.files_list_up{{
    padding: 10px 10px;
    background-color: {style.flup_bgcolor}; 
    color: {style.flup_fgcolor};
    font-size: medium;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}}

.files_list_down{{
    padding: 10px 10px;
    background-color: {style.fldown_bgcolor}; 
    color: {style.fldown_fgcolor};
    font-size: large;
    font-weight: bold;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}}

.topic{{
    color:{style.fgcolor};
    font-size: xxx-large;
    font-weight: bold;
    font-family:monospace;    
}}

.msg_login{{
    color: {style.msgcolor}; 
    font-size: large;
    font-weight: bold;
    font-family:monospace;    
    animation-duration: 3s; 
    animation-name: fader_msg;
}}
@keyframes fader_msg {{from {{color: {style.bgcolor};}} to {{color: {style.msgcolor}; }} }}



.topic_mid{{
    color: {style.fgcolor};
    font-size: x-large;
    font-style: italic;
    font-weight: bold;
    font-family:monospace;    
}}

.userword{{
    color: {style.fgcolor};
    font-weight: bold;
    font-family:monospace;    
    font-size: xxx-large;
}}


.upword{{
    color: {style.fgcolor};
    font-weight: bold;
    font-family:monospace;    
    font-size: xx-large;

}}

.status{{
    padding: 10px 10px;
    background-color: {style.item_bgcolor}; 
    color: {style.item_normal};
    font-size: medium;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}}


.files_status{{
    font-weight: bold;
    font-size: x-large;
    font-family:monospace;
}}


.admin_mid{{
    color: {style.fgcolor}; 
    font-size: x-large;
    font-weight: bold;
    font-family:monospace;    
    animation-duration: 10s;
}}
@keyframes fader_admin_failed {{from {{color: {style.item_false};}} to {{color: {style.fgcolor}; }} }}
@keyframes fader_admin_success {{from {{color: {style.item_true};}} to {{color: {style.fgcolor}; }} }}
@keyframes fader_admin_normal {{from {{color: {style.item_normal};}} to {{color: {style.fgcolor}; }} }}



.btn_enablel {{
    padding: 2px 10px 2px;
    color: {style.item_false}; 
    font-size: medium;
    border-radius: 2px;
    font-family:monospace;
    text-decoration: none;
}}


.btn_disablel {{
    padding: 2px 10px 2px;
    color: {style.item_true}; 
    font-size: medium;
    border-radius: 2px;
    font-family:monospace;
    text-decoration: none;
}}


""" + """

#file {
    border-style: solid;
    border-radius: 10px;
    font-family:monospace;
    background-color: #232323;
    border-color: #232323;
    color: #FFFFFF;
    font-size: small;
}
#submit {
    padding: 2px 10px 2px;
    background-color: #232323; 
    color: #FFFFFF;
    font-family:monospace;
    font-weight: bold;
    font-size: large;
    border-style: solid;
    border-radius: 10px;
    border-color: #232323;
    text-decoration: none;
    font-size: small;
}
#submit:hover {
  box-shadow: 0 12px 16px 0 rgba(0, 0, 0,0.24), 0 17px 50px 0 rgba(0, 0, 0,0.19);
}



.bridge{
    line-height: 2;
}



.txt_submit{

    text-align: left;
    font-family:monospace;
    border: 1px;
    background: rgb(218, 187, 255);
    appearance: none;
    position: relative;
    border-radius: 3px;
    padding: 5px 5px 5px 5px;
    line-height: 1.5;
    color: #8225c2;
    font-size: 16px;
    font-weight: 350;
    height: 24px;
}
::placeholder {
    color: #8225c2;
    opacity: 1;
    font-family:monospace;   
}

.txt_login{

    text-align: center;
    font-family:monospace;

    box-shadow: inset #abacaf 0 0 0 2px;
    border: 0;
    background: rgba(0, 0, 0, 0);
    appearance: none;
    position: relative;
    border-radius: 3px;
    padding: 9px 12px;
    line-height: 1.4;
    color: rgb(0, 0, 0);
    font-size: 16px;
    font-weight: 400;
    height: 40px;
    transition: all .2s ease;
    :hover{
        box-shadow: 0 0 0 0 #fff inset, #1de9b6 0 0 0 2px;
    }
    :focus{
        background: #fff;
        outline: 0;
        box-shadow: 0 0 0 0 #fff inset, #1de9b6 0 0 0 3px;
    }
}
::placeholder {
    color: #888686;
    opacity: 1;
    font-weight: bold;
    font-style: oblique;
    font-family:monospace;   
}


.txt_login_small{
    box-shadow: inset #abacaf 0 0 0 2px;
    text-align: center;
    font-family:monospace;
    border: 0;
    background: rgba(0, 0, 0, 0);
    appearance: none;
    position: absolute;
    border-radius: 3px;
    padding: 9px 12px;
    margin: 0px 0px 0px 4px;
    line-height: 1.4;
    color: rgb(0, 0, 0);
    font-size: 16px;
    font-weight: 400;
    height: 40px;
    width: 45px;
    transition: all .2s ease;
    :hover{
        box-shadow: 0 0 0 0 #fff inset, #1de9b6 0 0 0 2px;
    }
    :focus{
        background: #fff;
        outline: 0;
        box-shadow: 0 0 0 0 #fff inset, #1de9b6 0 0 0 3px;
    }
}




.btn_logout {
    padding: 2px 10px 2px;
    background-color: #060472; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.btn_refresh_small {
    padding: 2px 10px 2px;
    background-color: #6daa43; 
    color: #FFFFFF;
    font-size: small;
    border-style: none;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_refresh {
    padding: 2px 10px 2px;
    background-color: #6daa43; 
    color: #FFFFFF;
    font-size: large;
    font-weight: bold;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_purge {
    padding: 2px 10px 2px;
    background-color: #9a0808; 
    border-style: none;
    color: #FFFFFF;
    font-size: small;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_purge_large {
    padding: 2px 10px 2px;
    background-color: #9a0808; 
    border-style: none;
    color: #FFFFFF;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_submit {
    padding: 2px 10px 2px;
    background-color: #8225c2; 
    border-style: none;
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_report {
    padding: 2px 10px 2px;
    background-color: #c23f79; 
    border-style: none;
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}
.btn_admin {
    padding: 2px 10px 2px;
    background-color: #2b2b2b; 
    border-style: none;
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_store_actions {
    padding: 2px 2px 2px 2px;
    background-color: #FFFFFF; 
    border-style: solid;
    border-width: thin;
    border-color: #000000;
    color: #000000;
    font-weight: bold;
    font-size: medium;
    border-radius: 5px;
    font-family:monospace;
    text-decoration: none;
}

.btn_admin_actions {
    padding: 2px 10px 2px;
    background-color: #FFFFFF; 
    border-style: solid;
    border-width: medium;
    border-color: #000000;
    color: #000000;
    font-weight: bold;
    font-size: xxx-large;
    border-radius: 5px;
    font-family:monospace;
    text-decoration: none;
}


.btn_admin_actions .tooltiptext {
  visibility: hidden;

  background-color: #000000;
  color: #ffffff;
  text-align: center;
  font-size: large;
  border-radius: 6px;
  padding: 5px 15px 5px 15px;

  position: absolute;
  z-index: 1;
}

.btn_admin_actions:hover .tooltiptext {
  visibility: visible;
}


.btn_folder {
    padding: 2px 10px 2px;
    background-color: #934343; 
    border-style: none;
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
    line-height: 2;
}

.btn_board {
    padding: 2px 10px 2px;
    background-color: #934377; 
    border-style: none;
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.btn_login {
    padding: 2px 10px 2px;
    background-color: #060472; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
    border-style:  none;
}

.btn_download {
    padding: 2px 10px 2px;
    background-color: #089a28; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_store{
    padding: 2px 10px 2px;
    background-color: #10a58a; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_upload {
    padding: 2px 10px 2px;
    background-color: #0b7daa; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_home {
    padding: 2px 10px 2px;
    background-color: #a19636; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_enable {
    padding: 2px 10px 2px;
    background-color: #d30000; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.btn_disable {
    padding: 2px 10px 2px;
    background-color: #00d300; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


"""
)
# ******************************************************************************************

FAVICON=[
0,0,1,0,1,0,32,32,0,0,1,0,32,0,168,16,0,0,22,0,0,0,40,0,0,0,32,0,0,0,64,0,0,0,1,0,32,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,255,18,0,0,255,18,0,0,255,19,0,0,255,22,0,
0,255,22,0,0,255,8,0,0,255,47,0,0,255,17,0,0,255,4,0,0,255,18,0,0,255,18,0,0,255,22,0,0,255,13,0,0,255,14,0,
0,255,21,0,0,255,27,0,0,255,25,0,0,255,11,0,0,255,28,0,0,255,26,0,0,255,21,0,0,255,18,0,0,255,23,0,0,255,19,0,
0,255,16,0,0,255,15,0,0,255,22,0,0,255,20,0,0,255,18,0,0,255,9,0,0,255,13,0,0,255,19,0,0,255,15,0,0,255,11,0,
0,255,4,0,0,255,2,0,0,255,15,0,0,255,28,0,0,255,35,0,0,255,2,0,1,255,11,0,1,255,5,0,2,255,2,0,2,255,23,0,
1,255,19,0,0,255,18,0,0,255,19,0,0,255,24,0,0,255,37,0,0,255,29,0,1,255,9,0,1,255,24,0,1,255,26,0,1,255,31,0,
1,255,20,0,1,255,25,0,0,255,24,0,0,255,26,0,0,255,18,0,0,255,13,0,0,255,9,0,0,255,6,0,0,255,12,0,0,255,22,0,
0,255,31,0,0,255,35,0,0,255,25,0,0,255,8,0,0,255,10,0,0,255,40,0,1,255,8,0,3,255,9,0,5,255,5,0,5,255,3,0,
6,255,8,0,6,255,33,0,5,255,9,0,4,255,30,0,3,255,29,0,3,255,20,0,3,255,36,0,4,255,33,0,4,255,26,0,5,255,6,0,
6,255,24,0,6,255,24,0,5,255,18,0,4,255,24,0,3,255,27,0,1,255,18,0,0,255,15,0,0,255,4,0,0,255,2,0,0,255,8,0,
0,255,13,0,0,255,29,0,0,255,25,0,0,255,16,0,0,255,25,0,0,255,7,0,1,255,25,0,3,255,13,0,5,255,11,0,8,255,8,0,
11,255,18,0,13,255,8,0,14,255,13,0,13,255,29,0,11,255,22,0,9,255,33,0,7,255,22,0,6,255,33,0,6,255,33,0,8,255,33,0,
10,255,25,0,12,255,12,0,13,255,16,0,13,255,25,0,12,255,22,0,9,255,22,0,7,255,16,0,4,255,28,0,1,255,8,0,0,255,4,0,
0,255,3,0,0,255,4,0,0,255,10,0,0,255,29,0,0,255,21,0,0,255,23,0,0,255,16,0,1,255,3,0,4,255,7,0,7,255,16,0,
11,255,16,0,16,255,10,0,19,255,13,0,22,255,29,0,23,255,25,0,23,255,16,0,20,255,22,0,17,255,25,0,13,255,36,0,12,255,32,0,
12,255,11,0,15,255,10,0,18,255,8,0,21,255,9,0,23,255,10,0,23,255,27,0,21,255,43,0,18,255,50,0,13,255,22,0,9,255,31,0,
5,255,9,0,3,255,6,0,0,255,7,0,0,255,1,0,0,255,6,0,0,255,39,0,0,255,35,0,0,255,21,0,0,255,6,0,3,255,4,0,
7,255,14,0,12,255,16,0,19,255,19,0,25,255,13,0,31,255,13,0,35,255,32,0,37,255,25,0,35,255,13,0,31,255,23,0,25,255,38,0,
21,255,32,0,19,255,25,0,19,255,13,0,23,255,10,0,28,255,12,0,33,255,13,0,36,255,13,0,37,255,15,0,34,255,17,0,28,255,44,0,
22,255,22,0,15,255,27,0,9,255,14,0,4,255,9,0,1,255,6,0,0,255,11,0,0,255,10,0,0,255,33,0,0,255,22,0,0,255,11,0,
2,255,3,0,6,255,10,0,11,255,18,0,18,255,27,0,27,255,28,0,37,255,22,0,53,255,51,0,125,255,63,0,158,255,70,0,188,255,55,0,
137,255,33,0,36,255,17,0,30,255,33,0,27,255,14,0,28,255,12,0,33,255,23,0,63,255,59,0,161,255,73,0,200,255,51,0,138,255,33,0,
72,255,23,0,41,255,23,0,32,255,30,0,23,255,18,0,15,255,15,0,8,255,13,0,3,255,9,0,0,255,2,0,0,255,19,0,0,255,20,0,
0,255,19,0,0,255,10,0,3,255,15,0,8,255,18,0,16,255,14,0,25,255,16,0,37,255,40,0,101,255,77,0,212,255,71,0,195,255,77,0,
203,255,75,0,204,255,76,0,205,255,27,0,64,255,31,0,40,255,23,0,36,255,14,0,37,255,25,0,43,255,57,0,136,255,74,0,195,255,82,0,
225,255,74,0,203,255,72,0,195,255,65,0,176,255,17,0,45,255,20,0,31,255,17,0,20,255,16,0,12,255,12,0,6,255,9,0,2,255,9,0,
0,255,2,0,0,255,12,0,0,255,15,0,1,255,13,0,5,255,8,0,11,255,13,0,20,255,26,0,32,255,53,0,89,255,74,0,179,255,77,0,
200,255,70,0,182,255,77,0,208,255,81,0,224,255,68,0,179,255,50,1,109,255,32,2,49,255,18,1,44,255,20,1,46,255,43,1,52,255,75,0,
186,255,74,0,179,255,82,0,225,255,72,0,188,255,76,0,204,255,71,0,169,255,66,0,164,255,39,1,39,255,27,0,26,255,9,0,16,255,10,0,
8,255,10,0,3,255,18,0,0,255,12,0,0,255,10,0,0,255,17,0,3,255,30,0,7,255,43,0,14,255,52,0,24,255,54,0,38,255,66,0,
142,255,75,0,205,255,67,0,162,255,72,0,194,255,68,1,176,255,81,0,222,255,69,1,173,255,59,3,142,255,25,5,56,255,23,4,52,255,23,5,
53,255,32,3,72,255,70,0,181,255,77,0,198,255,75,0,197,255,72,0,188,255,66,0,163,255,77,0,205,255,75,0,181,255,58,0,79,255,25,0,
31,255,14,0,19,255,30,0,10,255,23,0,5,255,7,0,1,255,4,0,0,255,47,0,0,255,48,0,4,255,45,0,9,255,48,0,17,255,53,0,
28,255,46,0,45,255,78,0,214,255,70,0,183,255,57,0,148,255,81,0,224,255,80,0,217,255,70,1,176,255,75,0,199,255,65,2,162,255,38,9,
63,255,36,9,58,255,37,9,60,255,45,6,103,255,64,2,170,255,80,0,220,255,68,1,173,255,82,0,225,255,73,0,193,255,62,0,150,255,79,0,
211,255,58,0,134,255,19,0,35,255,30,0,22,255,31,0,12,255,30,0,6,255,31,0,1,255,20,0,0,255,11,0,1,255,8,0,4,255,11,0,
10,255,31,0,19,255,26,0,31,255,27,0,60,255,71,0,188,255,66,0,180,255,71,0,194,255,72,0,196,255,82,0,225,255,78,13,187,255,123,62,
231,255,69,3,179,255,40,12,66,255,42,12,62,255,106,91,126,255,51,7,123,255,72,1,195,255,61,2,161,255,79,0,217,255,79,0,218,255,66,0,
180,255,74,0,202,255,63,0,173,255,52,0,140,255,17,0,38,255,25,0,25,255,26,0,15,255,38,0,7,255,28,0,2,255,30,0,0,255,3,0,
2,255,3,0,6,255,7,0,13,255,14,0,22,255,27,0,35,255,29,0,49,255,68,0,162,255,77,0,200,255,73,0,197,255,66,1,165,255,76,0,
197,255,82,0,224,255,168,133,231,255,77,17,173,255,56,16,69,255,45,16,65,255,128,114,142,255,86,53,136,255,70,3,177,255,77,1,208,255,80,0,
219,255,65,1,173,255,68,0,185,255,75,0,203,255,71,0,191,255,38,0,102,255,15,0,42,255,26,0,28,255,23,0,18,255,42,0,10,255,13,0,
4,255,13,0,0,255,2,0,4,255,10,0,8,255,18,0,16,255,40,0,26,255,24,0,40,255,29,0,54,255,37,0,68,255,46,1,82,255,49,2,
91,255,54,2,109,255,69,1,178,255,70,2,186,255,101,47,194,255,122,89,171,255,57,18,68,255,69,19,65,255,50,24,70,255,150,135,168,255,77,5,
195,255,73,2,187,255,69,1,184,255,59,2,150,255,48,3,96,255,63,1,87,255,57,1,75,255,48,1,61,255,42,0,47,255,50,0,33,255,17,0,
21,255,30,0,12,255,30,0,5,255,5,0,2,255,8,0,6,255,19,0,11,255,19,0,20,255,27,0,32,255,26,0,47,255,39,0,92,255,46,0,
106,255,45,1,98,255,52,3,95,255,60,4,97,255,50,5,98,255,47,7,106,255,53,8,126,255,156,140,177,255,65,37,81,255,116,92,123,255,80,50,
89,255,56,29,80,255,149,119,185,255,72,21,126,255,51,6,99,255,54,5,98,255,49,4,97,255,46,2,93,255,62,0,101,255,63,0,102,255,54,0,
67,255,34,0,39,255,12,0,26,255,19,0,16,255,42,0,8,255,9,0,3,255,19,0,7,255,24,0,15,255,27,0,26,255,25,0,39,255,56,0,
145,255,82,0,225,255,82,0,225,255,81,0,224,255,79,0,216,255,79,0,215,255,81,0,222,255,81,0,224,255,74,1,200,255,115,75,178,255,117,88,
118,255,139,120,142,255,87,67,100,255,153,139,164,255,155,122,211,255,116,54,224,255,112,46,228,255,79,0,217,255,77,0,210,255,80,0,220,255,82,0,
225,255,82,0,225,255,79,0,216,255,27,0,64,255,12,0,33,255,17,0,20,255,50,0,11,255,18,0,4,255,17,0,10,255,15,0,19,255,14,0,
32,255,18,0,47,255,61,0,168,255,82,0,225,255,82,0,225,255,82,0,225,255,82,0,225,255,82,0,225,255,80,0,218,255,71,1,184,255,77,0,
209,255,54,10,98,255,121,97,123,255,61,38,70,255,86,62,92,255,37,18,61,255,81,26,175,255,89,24,196,255,74,1,198,255,82,0,225,255,82,0,
225,255,82,0,225,255,82,0,225,255,82,0,225,255,81,0,224,255,37,0,83,255,16,0,39,255,28,0,25,255,49,0,15,255,20,0,7,255,26,0,
13,255,31,0,24,255,26,1,38,255,20,0,54,255,36,0,90,255,59,0,159,255,71,0,187,255,77,0,198,255,77,0,197,255,68,0,176,255,70,0,
184,255,81,0,224,255,65,4,145,255,42,11,57,255,37,18,51,255,30,14,46,255,88,75,99,255,45,16,53,255,44,12,77,255,77,1,208,255,77,0,
208,255,65,1,174,255,70,0,190,255,75,0,201,255,72,0,196,255,66,0,178,255,57,0,134,255,34,1,63,255,19,0,46,255,16,0,30,255,34,0,
18,255,16,0,9,255,12,0,16,255,30,0,28,255,24,0,42,255,50,0,137,255,81,0,223,255,79,0,216,255,77,0,207,255,71,0,159,255,71,0,
151,255,79,0,213,255,82,0,225,255,72,0,183,255,54,5,70,255,25,7,47,255,24,9,38,255,34,9,36,255,47,24,50,255,84,68,93,255,57,10,
61,255,53,7,106,255,81,0,222,255,81,0,224,255,68,0,185,255,51,0,134,255,72,0,193,255,76,0,209,255,80,0,221,255,76,0,207,255,25,0,
65,255,13,0,35,255,11,0,21,255,12,0,12,255,15,0,18,255,32,0,30,255,19,0,45,255,60,0,164,255,82,0,225,255,76,0,208,255,70,0,
170,255,78,0,205,255,82,0,225,255,82,0,225,255,76,0,204,255,58,2,83,255,37,2,53,255,20,3,36,255,19,6,29,255,21,6,26,255,30,7,
28,255,105,84,102,255,68,23,59,255,66,6,71,255,56,2,134,255,81,0,224,255,82,0,225,255,81,0,222,255,68,0,183,255,67,0,181,255,81,0,
222,255,81,0,224,255,29,0,79,255,14,0,37,255,11,0,24,255,13,0,13,255,31,0,19,255,15,0,31,255,25,0,69,255,57,0,155,255,75,0,
196,255,77,0,203,255,79,0,212,255,82,0,225,255,82,0,225,255,77,0,211,255,51,1,92,255,49,2,58,255,26,0,37,255,21,1,27,255,12,2,
20,255,11,1,18,255,12,2,20,255,20,6,25,255,35,9,37,255,37,2,48,255,53,3,68,255,60,0,152,255,81,0,224,255,82,0,225,255,82,0,
225,255,74,0,200,255,75,0,204,255,66,0,179,255,45,0,120,255,14,0,38,255,9,0,24,255,5,0,14,255,14,0,18,255,13,0,28,255,65,0,
174,255,82,0,225,255,81,0,222,255,74,0,184,255,82,0,225,255,82,0,225,255,74,0,199,255,50,1,91,255,47,1,55,255,36,0,37,255,26,0,
26,255,18,0,18,255,12,0,13,255,9,0,11,255,9,0,12,255,13,0,16,255,15,1,23,255,21,1,33,255,29,1,47,255,53,2,65,255,62,0,
142,255,81,0,222,255,82,0,225,255,79,0,217,255,71,0,190,255,82,0,225,255,81,0,224,255,29,0,79,255,9,0,23,255,6,0,13,255,19,0,
15,255,36,0,24,255,60,0,143,255,64,0,166,255,59,0,96,255,64,0,128,255,64,0,155,255,57,0,110,255,42,1,59,255,39,0,45,255,51,0,
34,255,51,0,25,255,26,0,17,255,20,0,11,255,14,0,7,255,11,0,6,255,15,0,7,255,17,0,10,255,10,0,15,255,10,0,22,255,18,0,
30,255,32,1,39,255,47,1,53,255,38,1,78,255,50,0,135,255,62,0,166,255,33,1,80,255,56,0,138,255,65,0,178,255,26,0,69,255,8,0,
20,255,18,0,12,255,28,0,12,255,25,0,19,255,16,0,27,255,45,0,50,255,64,0,126,255,55,0,100,255,42,1,44,255,42,0,41,255,33,0,
36,255,36,0,30,255,21,0,22,255,24,0,16,255,28,0,10,255,17,0,6,255,12,0,4,255,14,0,2,255,16,0,3,255,20,0,5,255,4,0,
9,255,6,0,14,255,9,0,19,255,12,0,26,255,13,0,33,255,15,0,39,255,17,0,43,255,20,0,55,255,51,0,127,255,44,0,99,255,22,0,
31,255,9,0,23,255,7,0,16,255,23,0,9,255,15,0,8,255,19,0,14,255,42,0,19,255,35,0,24,255,34,0,27,255,35,0,29,255,45,0,
29,255,42,0,27,255,29,0,23,255,16,0,18,255,8,0,13,255,5,0,9,255,5,0,5,255,4,0,3,255,18,0,0,255,16,0,0,255,13,0,
0,255,15,0,2,255,8,0,4,255,9,0,7,255,9,0,11,255,11,0,16,255,12,0,20,255,14,0,25,255,15,0,28,255,12,0,29,255,12,0,
29,255,22,0,26,255,27,0,22,255,11,0,16,255,8,0,11,255,8,0,6,255,35,0,5,255,44,0,8,255,29,0,11,255,23,0,15,255,24,0,
17,255,39,0,18,255,36,0,17,255,27,0,15,255,22,0,13,255,16,0,10,255,17,0,6,255,31,0,4,255,14,0,2,255,1,0,0,255,18,0,
0,255,6,0,0,255,13,0,0,255,2,0,0,255,1,0,1,255,2,0,3,255,8,0,5,255,11,0,8,255,12,0,11,255,14,0,14,255,17,0,
17,255,19,0,18,255,14,0,18,255,7,0,16,255,9,0,13,255,8,0,10,255,3,0,6,255,10,0,4,255,35,0,2,255,29,0,4,255,28,0,
5,255,31,0,7,255,30,0,8,255,35,0,9,255,27,0,8,255,35,0,8,255,34,0,6,255,27,0,4,255,40,0,1,255,26,0,1,255,27,0,
0,255,14,0,0,255,10,0,0,255,18,0,0,255,18,0,0,255,11,0,0,255,21,0,0,255,16,0,0,255,14,0,1,255,5,0,3,255,2,0,
5,255,13,0,6,255,21,0,8,255,18,0,9,255,16,0,9,255,9,0,8,255,4,0,7,255,2,0,4,255,1,0,3,255,2,0,1,255,21,0,
0,255,25,0,1,255,31,0,2,255,36,0,2,255,27,0,3,255,25,0,4,255,29,0,3,255,32,0,3,255,44,0,1,255,42,0,0,255,33,0,
0,255,24,1,0,255,22,0,0,255,26,0,0,255,12,0,0,255,24,0,0,255,4,0,0,255,17,0,0,255,22,0,0,255,20,0,0,255,22,0,
0,255,24,0,0,255,19,0,1,255,7,0,2,255,7,0,3,255,5,0,4,255,14,0,4,255,18,0,3,255,15,0,2,255,12,0,1,255,5,0,
0,255,1,0,0,255,25,1,0,255,29,0,0,255,42,0,0,255,36,0,0,255,27,0,0,255,30,0,0,255,29,0,0,255,26,0,0,255,48,0,
0,255,44,0,0,255,26,0,0,255,37,0,0,255,35,0,0,255,24,0,0,255,27,0,0,255,15,0,0,255,15,0,0,255,18,0,0,255,20,0,
0,255,20,0,0,255,20,0,0,255,19,0,0,255,20,0,0,255,23,0,0,255,7,0,0,255,3,0,0,255,17,0,0,255,10,0,0,255,11,0,
0,255,5,0,0,255,9,0,0,255,11,0,0,255,28,0,0,255,18,0,0,255,27,0,0,255,28,0,0,255,34,0,0,255,33,0,0,255,23,0,
0,255,26,0,0,255,45,0,0,255,30,0,0,255,32,0,0,255,20,0,0,255,17,0,0,255,25,0,0,255,26,0,0,255,25,0,0,255,19,0,
0,255,20,0,0,255,21,0,0,255,21,0,0,255,14,0,0,255,8,0,0,255,12,0,0,255,19,0,0,255,21,0,0,255,3,0,0,255,12,0,
0,255,13,0,0,255,7,0,0,255,32,0,0,255,43,0,0,255,41,0,0,255,47,0,0,255,33,0,0,255,26,0,0,255,27,0,0,255,28,0,
0,255,19,0,0,255,26,0,0,255,24,0,0,255,29,0,0,255,26,0,0,255,17,0,0,255,14,0,0,255,11,0,0,255,11,0,0,255,17,0,
0,255,27,0,0,255,20,0,0,255,15,0,0,255,22,0,0,255,42,0,0,255,39,0,0,255,22,0,0,255,2,0,0,255,4,0,0,255,18,0,
0,255,19,0,0,255,9,0,0,255,17,0,0,255,18,0,0,255,40,0,0,255,29,0,0,255,31,0,0,255,34,0,0,255,29,0,0,255,25,0,
0,255,24,0,0,255,10,0,0,255,17,0,0,255,21,0,0,255,24,0,0,255,24,0,0,255,17,0,0,255,10,0,0,255,2,0,0,255,5,0,
0,255,8,0,0,255,8,0,0,255,17,0,0,255,30,0,0,255,34,0,0,255,23,0,0,255,30,0,0,255,17,0,0,255,27,0,0,255,23,0,
0,255,8,0,0,255,5,0,0,255,20,0,0,255,23,0,0,255,22,0,0,255,18,0,0,255,26,0,0,255,25,0,0,255,25,0,0,255,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
]

for k,v in HTML_TEMPLATES.items():
    h = os.path.join(HTMLDIR, f"{k}.html")
    if (not os.path.isfile(h)) or bool(parsed.cos):
        with open(h, 'w', encoding='utf-8') as f: f.write(v)
for k,v in CSS_TEMPLATES.items():
    h = os.path.join(HTMLDIR, f"{k}.css")
    if (not os.path.isfile(h)) or bool(parsed.cos):
        with open(h, 'w', encoding='utf-8') as f: f.write(v)
sprint(f'↪ Created html/css templates @ {HTMLDIR}')

with open( os.path.join(HTMLDIR, f"favicon.ico") , 'wb') as f: f.write((b''.join([i.to_bytes() for i in FAVICON])))

# delete pages dict after creation? #- keep the keys to "coe"
HTML_TEMPLATES = tuple(HTML_TEMPLATES.keys()) #{k:None for k in HTML_TEMPLATES} 
CSS_TEMPLATES = tuple(CSS_TEMPLATES.keys()) #{k:None for k in CSS_TEMPLATES}
del FAVICON

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
# validation
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

# = { k : [vu,  vn, 0.0, ''] for k,(va,vu,vn,_) in db.items() if '-' not in va} 
# -----------------------------------------------------------------------------------------
#print(dbsub)
def GetUserFiles(uid): 
    if not REQUIRED_FILES: return True # no files are required to be uploaded
    udir = os.path.join( app.config['uploads'], uid)
    has_udir = os.path.isdir(udir)
    if has_udir: return not (False in [os.path.isfile(os.path.join(udir, f)) for f in REQUIRED_FILES])
    else: return False

# ------------------------------------------------------------------------------------------
# application setting and instance
# ------------------------------------------------------------------------------------------

app = Flask(
    __name__,
    static_folder=HTMLDIR,      # Set your custom static folder path here
    template_folder=HTMLDIR,   # Set your custom templates folder path here
    instance_relative_config = True,
    instance_path = WORKDIR,
)

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
# ------------------------------------------------------------------------------------------
class UploadFileForm(FlaskForm): # The upload form using FlaskForm
    file = MultipleFileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
# ------------------------------------------------------------------------------------------

#%% [4]
# app.route  > all app.route implemented here 
# ------------------------------------------------------------------------------------------
# login
# ------------------------------------------------------------------------------------------
@app.route('/', methods =['GET', 'POST'])
def route_login():
    LOGIN_NEED_TEXT =       '🔒'
    LOGIN_FAIL_TEXT =       '❌'     
    LOGIN_NEW_TEXT =        '🔥'
    LOGIN_CREATE_TEXT =     '🔑'    
    #NAME, PASS = 2, 3
    global db#, HAS_PENDING#<--- only when writing to global wariables
    if request.method == 'POST' and 'uid' in request.form and 'passwd' in request.form:
        in_uid = f"{request.form['uid']}"
        in_passwd = f"{request.form['passwd']}"
        in_name = f'{request.form["named"]}' if 'named' in request.form else ''
        in_emoji = f'{request.form["emojid"]}' if 'emojid' in request.form else app.config['emoji']
        if ((not in_emoji) or (app.config['rename']<2)): in_emoji = app.config['emoji']
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
                        #HAS_PENDING+=1
                        if in_name!=named and valid_name and (app.config['rename']>0) : 
                            db[uid][2]=in_name
                            #HAS_PENDING+=1
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
                        session['admind'] = admind + APPEND_ACCESS
                        session['filed'] = os.listdir(folder_name)
                        session['reported'] = sorted(os.listdir(folder_report))
                        session['emojid'] = in_emoji 
                        session['hidden_store'] = False
                        session['hidden_storeuser'] = True
                        
                        if in_name!=named and  valid_name and  (app.config['rename']>0): 
                            session['named'] = in_name
                            db[uid][2] = in_name
                            #HAS_PENDING+=1
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

@app.route('/new', methods =['GET', 'POST'])
def route_new():
    if not app.config['reg']: return "registration is not allowed"
    LOGIN_NEED_TEXT =       '👤'
    LOGIN_FAIL_TEXT =       '❌'     
    LOGIN_NEW_TEXT =        '🔥'
    LOGIN_CREATE_TEXT =     '🔑'    
    #NAME, PASS = 2, 3
    global db#, HAS_PENDING#<--- only when writing to global wariables
    if request.method == 'POST' and 'uid' in request.form and 'passwd' in request.form:
        in_uid = f"{request.form['uid']}"
        in_passwd = f"{request.form['passwd']}"
        in_name = f'{request.form["named"]}' if 'named' in request.form else ''
        in_emoji = f'{request.form["emojid"]}' if 'emojid' in request.form else app.config['emoji']
        if ((not in_emoji) or (app.config['rename']<2)): in_emoji = app.config['emoji']
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
        warn = LOGIN_NEED_TEXT 
        
    return render_template('new.html', msg = msg,  warn = warn)

@app.route('/logout')
def route_logout():
    r""" logout a user and redirect to login page """
    if not session.get('has_login', False):  return redirect(url_for('route_login'))
    if not session.get('uid', False): return redirect(url_for('route_login'))
    if session['has_login']:  dprint(f'● {session["uid"]} {session["emojid"]} {session["named"]} has logged out via {request.remote_addr}') 
    else: dprint(f'✗ {session["uid"]} ◦ {session["named"]} was removed due to invalid uid ({session["uid"]}) via {request.remote_addr}') 
    # session['has_login'] = False
    # session['uid'] = ""
    # session['named'] = ""
    # session['emojid'] = ""
    # session['admind'] = ''
    # session['filed'] = []
    session.clear()
    return redirect(url_for('route_login'))
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# board
# ------------------------------------------------------------------------------------------
@app.route('/board', methods =['GET'])
def route_board():
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if 'B' not in session['admind']:  return redirect(url_for('route_home'))
    return BOARD_PAGE

# ------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------
# download
# ------------------------------------------------------------------------------------------
@app.route('/downloads', methods =['GET'], defaults={'req_path': ''})
@app.route('/downloads/<path:req_path>')
def route_downloads(req_path):
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if 'D' not in session['admind']:  return redirect(url_for('route_home'))
    abs_path = os.path.join(app.config['downloads'], req_path) # Joining the base and the requested path
    if not os.path.exists(abs_path): 
        dprint(f"⇒ requested file was not found {abs_path}") #Return 404 if path doesn't exist
        return abort(404) # (f"◦ requested file was not found") #Return 404 if path doesn't exist
    if os.path.isfile(abs_path):  #(f"◦ sending file ")
        dprint(f'● {session["uid"]} ◦ {session["named"]} just downloaded the file {req_path} via {request.remote_addr}')
        return send_file(abs_path) # Check if path is a file and serve
    return render_template('downloads.html')
# ------------------------------------------------------------------------------------------

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
    #except: return abort(404)
    #return send_file(fp)


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

                        # end for
                    

                        #status, success = f"Updated Evaluation by file [{sf}]", True
                        #dprint(f'✓ {session["uid"]} ◦ {session["named"]} just uploaded {sf}') 
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

class HConv:
    # html converters
    @staticmethod
    def convert(abs_path):
        new_abs_path = f'{abs_path}.html'
        if abs_path.lower().endswith(".ipynb"):
            if not has_nbconvert_package: return False, f"missing package - nbconvert"
            try:
                x = __class__.nb2html( abs_path )
                with open(new_abs_path, 'w') as f: f.write(x)
                return True, (f"rendered Notebook to HTML @ {new_abs_path}")
            except: return False, (f"failed to rendered Notebook to HTML @ {new_abs_path}") 
        else: return False, (f"no renderer exists for {abs_path}")
        return False, "unknown"

    NB_STYLE_CSS = """<style type="text/css">

    .btn_header {
        background-color: #FFFFFF; 
        margin: 0px 0px 0px 6px;
        padding: 12px 6px 12px 6px;
        border-style: solid;
        border-width: thin;
        border-color: #000000;
        color: #000000;
        font-weight: bold;
        font-size: medium;
        border-radius: 5px;
    }

    .btn_actions {
        background-color: #FFFFFF; 
        padding: 2px 2px 2px 2px;
        margin: 5px 5px 5px 5px;
        border-style: solid;
        border-color: silver;
        border-width: thin;
        color: #000000;
        font-weight: bold;
        font-size: medium;
        border-radius: 2px;

    }
    </style>
    """

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

        fstart = f'<body'
        istart = page.find(fstart)
        if istart<0: return None
        page = f'{page[:istart]}{__class__.NB_STYLE_CSS}{page[istart:]}'

        fstart = f'</body'
        istart = page.find(fstart)
        if istart<0: return None
        ins= f'<hr><br><div align="left"><a class="btn_actions" href="#">🔝</a></div>'
        page = f'{page[:istart]}{ins}{page[istart:]}'


        return  page

def list_store_dir(abs_path):
    dirs, files = [], []
    with os.scandir(abs_path) as it:
        for item in it:
            if item.is_file(): files.append((item.name, item.name.startswith(".")))
            elif item.is_dir(): dirs.append((item.name, item.name.startswith(".")))
            else: pass
    return dirs, files



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
            hstatus, hmsg = HConv.convert(abs_path)
            dprint(f"{TABLINE}{'... ✓' if hstatus else '... ✗'} {hmsg}")
            return redirect(url_for('route_storeuser', subpath=os.path.dirname(subpath))) 
        else: 
            dprint(f"● {session['uid']} ◦ {session['named']} downloaded {subpath} from user-store via {request.remote_addr}")
            return send_file(abs_path, as_attachment=("get" in request.args))
    else: return abort(404)


# ------------------------------------------------------------------------------------------
# administrative
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
@app.route('/admin/', methods =['GET'], defaults={'req_cmd': ''})
@app.route('/admin/<req_cmd>')
def route_adminpage(req_cmd):
    r""" opens admin page """ 
    if not session.get('has_login', False): return redirect(url_for('route_login')) # "Not Allowed - Requires Login"
    in_cmd = f'{req_cmd}'
    if '+' in session['admind']: 
        if in_cmd: 
            if   in_cmd=="ref_downloads": STATUS, SUCCESS = update_dl()
            elif in_cmd=="db_write": STATUS, SUCCESS = persist_db()
            elif in_cmd=="db_read": STATUS, SUCCESS = reload_db()
            elif in_cmd=="ref_board": STATUS, SUCCESS = refresh_board()
            else: STATUS, SUCCESS =  f"Invalid command '{in_cmd}'", False
        else: STATUS, SUCCESS =  f"Admin Access is Enabled", True
    else: 
        if in_cmd: STATUS, SUCCESS =  f"This action requires Admin access", False
        else:  STATUS, SUCCESS =  f"Admin Access is Disabled", False
    return render_template('admin.html',  status=STATUS, success=SUCCESS)

def update_dl():
    r""" refreshes the  downloads"""
    app.config['dfl'] = GET_FILE_LIST(DOWNLOAD_FOLDER_PATH)
    dprint(f"▶ {session['uid']} ◦ {session['named']} just refreshed the download list via {request.remote_addr}")
    return "Updated download-list", True #  STATUS, SUCCESS



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
    if write_evaldb_to_disk(dbsub, verbose=False): 
        #dprint(f"▶ {session['uid']} ◦ {session['named']} just persisted the eval-db to disk via {request.remote_addr}")
        STATUS, SUCCESS = "Persisted db to disk", True
    else: STATUS, SUCCESS =  f"Write error, file might be open", False
    return STATUS, SUCCESS 

def reload_db():
    r""" reloads db from disk """
    global db, dbsub#, HAS_PENDING
    db = read_logindb_from_disk()
    dbsub = read_evaldb_from_disk()
    #HAS_PENDING=0
    dprint(f"▶ {session['uid']} ◦ {session['named']} just reloaded the db from disk via {request.remote_addr}")
    return "Reloaded db from disk", True #  STATUS, SUCCESS

def refresh_board():
    r""" refreshes the  board"""
    if update_board():
        dprint(f"▶ {session['uid']} ◦ {session['named']} just refreshed the board via {request.remote_addr}")
        return "Board was refreshed", True
    else: return "Board not enabled", False


# ------------------------------------------------------------------------------------------
# password reset
# ------------------------------------------------------------------------------------------
@app.route('/x/', methods =['GET'], defaults={'req_uid': ''})
@app.route('/x/<req_uid>')
def route_repass(req_uid):
    r""" reset user password"""
    if not session.get('has_login', False): return redirect(url_for('route_login')) # "Not Allowed - Requires Login"
    if app.config['repass']:
        if ('+' in session['admind']): 
            in_uid = f'{req_uid}'
            if in_uid: 
                in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
                global db#, HAS_PENDING
                record = db.get(in_query, None)
                if record is not None: 
                    admind, uid, named, _ = record
                    if ('+' not in admind) or (session['uid']==uid):
                        db[uid][3]='' ## 3 for PASS  record['PASS'].values[0]=''
                        #HAS_PENDING+=1
                        dprint(f"▶ {session['uid']} ◦ {session['named']} just reset the password for {uid} ◦ {named} via {request.remote_addr}")
                        STATUS, SUCCESS =  f"Password was reset for {uid} {named}", True
                    else: STATUS, SUCCESS =  f"You cannot reset password for account '{in_query}'", False
                else: STATUS, SUCCESS =  f"User '{in_query}' not found", False
            else: STATUS, SUCCESS =  f"User-id was not provided", False
        else: STATUS, SUCCESS =  "You are not allow to reset passwords", False
    else: STATUS, SUCCESS =  "Password reset is disabled for this session", False
    return render_template('admin.html',  status=STATUS, success=SUCCESS)
# ------------------------------------------------------------------------------------------
@app.route('/xx/', methods =['GET'], defaults={'req_uid': ''})
@app.route('/xx/<req_uid>')
def route_repassx(req_uid):
    r""" reset user password"""
    if not session.get('has_login', False): return redirect(url_for('route_login')) # "Not Allowed - Requires Login"
    form = UploadFileForm()
    results = []
    if app.config['repass']:
        if ('X' in session['admind']) or ('+' in session['admind']):
            in_uid = f'{req_uid}'
            if in_uid: 
                in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
                record = db.get(in_query, None)
                if record is not None: 
                    admind, uid, named, _ = record
                    if (('X' not in admind) and ('+' not in admind)) or (session['uid']==uid):
                        db[uid][3]='' ## 3 for PASS  record['PASS'].values[0]=''
                        #HAS_PENDING+=1
                        dprint(f"▶ {session['uid']} ◦ {session['named']} just reset the password for {uid} ◦ {named} via {request.remote_addr}")
                        STATUS, SUCCESS =  f"Password was reset for {uid} {named}", True
                    else: STATUS, SUCCESS =  f"You cannot reset password for account '{in_query}'", False
                else: STATUS, SUCCESS =  f"User '{in_query}' not found", False
            else: STATUS, SUCCESS =  f"User-id was not provided", False
        else: STATUS, SUCCESS =  "You are not allow to reset passwords", False
    else: STATUS, SUCCESS =  "Password reset is disabled for this session", False
    return render_template('evaluate.html',  status=STATUS, success=SUCCESS, form=form, results=results)
# ------------------------------------------------------------------------------------------


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#<-------------------DO NOT WRITE ANY NEW CODE AFTER THIS
#%% Server Section
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

# endpoint = f'{args.host}:{args.port}' if args.host!='0.0.0.0' else f'localhost:{args.port}'
# sprint(f'◉ http://{endpoint}')
# start_time = datetime.datetime.now()
# sprint('◉ start server @ [{}]'.format(start_time))
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
#<-------------------DO NOT WRITE ANY CODE AFTER THIS
end_time = datetime.datetime.now()
sprint('◉ stop server @ [{}]'.format(end_time))
sprint('↷ persisted login-db [{}]'.format(write_logindb_to_disk(db)))
sprint('↷ persisted eval-db [{}]'.format(write_evaldb_to_disk(dbsub)))

if bool(parsed.coe):
    sprint(f'↪ Cleaning up html/css templates...')
    try:
        for k in HTML_TEMPLATES:#.items():
            h = os.path.join(HTMLDIR, f"{k}.html")
            if  os.path.isfile(h) : os.remove(h)
        #sprint(f'↪ Removing css templates @ {STATIC_DIR}')
        for k in CSS_TEMPLATES:#.items():
            h = os.path.join(HTMLDIR, f"{k}.css")
            if os.path.isfile(h): os.remove(h)
        #os.removedirs(TEMPLATES_DIR)
        #os.removedirs(STATIC_DIR)
        sprint(f'↪ Removed html/css templates @ {HTMLDIR}')
    except:
        sprint(f'↪ Could not remove html/css templates @ {HTMLDIR}')
sprint('◉ server up-time was [{}]'.format(end_time - start_time))
sprint(f'...Finished!')
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@