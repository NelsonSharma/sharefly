__doc__="""
sharefly - a flask-based web app for sharing files.
"""


#-----------------------------------------------------------------------------------------
# NOTE: Checking run instance
#-----------------------------------------------------------------------------------------
from sys import exit
if __name__!='__main__': exit(f'[!] can not import {__name__}.{__file__}')
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
# NOTE: Imports
#-----------------------------------------------------------------------------------------
import os, argparse, getpass, logging, importlib.util
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
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# NOTE: args parsing
# ------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--dir', type=str, default='', help="path of workspace directory")
parser.add_argument('--verbose', type=int, default=2, help="verbose level in logging")
parser.add_argument('--log', type=str, default='', help="path of log file - keep blank to disable logging")


parser.add_argument('--reg', type=str, default='', help="if specified, allow users to register with specified access string such as DABU or DABUS+")
parser.add_argument('--cos', type=int, default=1, help="use 1 to create-on-start - create (overwrites) pages")
parser.add_argument('--coe', type=int, default=0, help="use 1 to clean-on-exit - deletes pages")

# appends access
parser.add_argument('--access', type=str, default='', help="if specified, allow users to append access string such as DABU or DABUS+ for this run only")

# dont change below
parser.add_argument('--config',  type=str, default='config', help="name of the config module")
parser.add_argument('--configd', type=str, default='default', help="config dict name")

parsed = parser.parse_args()
# ------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
# NOTE: Logfiles
#-----------------------------------------------------------------------------------------
LOGFILE = f'{parsed.log}'                               # define log dir - contains all logs
if LOGFILE and parsed.verbose>0: 
    try:
        # Set up logging to a file
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
# NOTE: verbose levels
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






















#-----------------------------------------------------------------------------------------
# NOTE: Start
#-----------------------------------------------------------------------------------------
PYDIR = os.path.dirname(__file__) # script directory of __main__.py
sprint(f'Starting...')
sprint(f'↪ Module @ {PYDIR}')
sprint(f'↪ Logging @ {LOGFILE}')


#-----------------------------------------------------------------------------------------
# NOTE: Check if workdir exists
#-----------------------------------------------------------------------------------------
WORKDIR = f'{parsed.dir}'                               # define working dir - contains all bases
if not WORKDIR: WORKDIR = os.getcwd()                   # if still not specified, set as getcwd
try: os.makedirs(WORKDIR, exist_ok=True)
except: fexit(f'[!] Workspace directory was not found and could not be created')
sprint(f'↪ Workspace directory is {WORKDIR}')
#-----------------------------------------------------------------------------------------
# ==> read configurations from the workdir
#-----------------------------------------------------------------------------------------
CONFIG = parsed.configd if parsed.configd else 'default' # the config-dict to read from
CONFIG_MODULE = parsed.config if parsed.config else None  # the name of configs module
if CONFIG_MODULE is None: fexit(f'[!] Config moudule name was not specified')
CONFIGS_FILE = f'{CONFIG_MODULE}.py' # the name of configs file
#-----------------------------------------------------------------------------------------
# try to import configs
# inside the WORKDIR there should be 'configs.py' file
# check if 'configs.py` exsists or not`
#-----------------------------------------------------------------------------------------
CONFIGS_FILE_PATH = os.path.join(WORKDIR, CONFIGS_FILE) # should exsist under workdir
if not os.path.isfile(CONFIGS_FILE_PATH):
    sprint(f'↪ Creating default config "{CONFIGS_FILE}" ...')
    # create default config
    with open(CONFIGS_FILE_PATH, 'w') as fw: 
        with open(os.path.join(PYDIR, 'config.py'), 'r') as fr: 
            fw.write(fr.read())
try: 
    # Load the module from the specified file path
    c_spec = importlib.util.spec_from_file_location(CONFIG_MODULE, CONFIGS_FILE_PATH)
    c_module = importlib.util.module_from_spec(c_spec)
    c_spec.loader.exec_module(c_module)
    sprint(f'↪ Imported config-module "{CONFIG_MODULE}" from {c_module.__file__}')
except: fexit(f'[!] Could import configs module "{CONFIG_MODULE}" at "{CONFIGS_FILE_PATH[:-3]}"')
try:
    sprint(f'↪ Reading config from {CONFIG_MODULE}.{CONFIG}')
    config_dict = getattr(c_module, CONFIG)
except:
    fexit(f'[!] Could not read config from {CONFIG_MODULE}.{CONFIG}')

if not isinstance(config_dict, dict): 
    try: config_dict=config_dict()
    except: pass
if not isinstance(config_dict, dict): raise fexit(f'Expecting a dict object for config')

from . import Fake
try: 
    sprint(f'↪ Building config from {CONFIG_MODULE}.{CONFIG}')
    args = Fake(**config_dict)
except: fexit(f'[!] Could not read config')
if not len(args): fexit(f'[!] Empty or Invalid config provided')
# ******************************************************************************************

# Read base dir first 
BASEDIR = os.path.abspath(((os.path.join(WORKDIR, args.base)) if args.base else WORKDIR))
try:     os.makedirs(BASEDIR, exist_ok=True)
except:  fexit(f'[!] base directory  @ {BASEDIR} was not found and could not be created') 
sprint(f'⚙ Base dicectiry: {BASEDIR}')


    

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


APPEND_ACCESS = f'{parsed.access}'.strip().upper()
from . import FileValidator, str2bytes, DISPLAY_SIZE_READABLE
FV=FileValidator(args.ext, args.required)


MAX_UPLOAD_SIZE = str2bytes(args.maxupsize)     # maximum upload file size 
MAX_UPLOAD_COUNT = ( inf if args.maxupcount<0 else args.maxupcount )       # maximum number of files that can be uploaded by one user
INITIAL_UPLOAD_STATUS = []           # a list of notes to be displayed to the users about uploading files
if FV.REQUIRED_FILES: INITIAL_UPLOAD_STATUS.append((-1, f'accepted files [{len(FV.REQUIRED_FILES)}]: {FV.REQUIRED_FILES}'))
else:
    if FV.ALLOWED_EXTENSIONS:  INITIAL_UPLOAD_STATUS.append((-1, f'allowed extensions [{len(FV.ALLOWED_EXTENSIONS)}]: {FV.ALLOWED_EXTENSIONS}'))
INITIAL_UPLOAD_STATUS.append((-1, f'max upload size: {DISPLAY_SIZE_READABLE(MAX_UPLOAD_SIZE)}'))
if not (MAX_UPLOAD_COUNT is inf): INITIAL_UPLOAD_STATUS.append((-1, f'max upload count: {MAX_UPLOAD_COUNT}'))
sprint(f'⚙ Upload Settings ({len(INITIAL_UPLOAD_STATUS)})')
for s in INITIAL_UPLOAD_STATUS: sprint(f' ⇒ {s[1]}')
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# WEB-SERVER INFORMATION
# ------------------------------------------------------------------------------------------\
from . import GET_SECRET_KEY
APP_SECRET_KEY =  GET_SECRET_KEY()


TEMPLATES_DIR, STATIC_DIR = os.path.join(PYDIR, "templates"), os.path.join(PYDIR, "static")
if parsed.cos:
    from .pages import make_pages
    sprint(f'↪ Creating html/css templates @ {PYDIR}')
    make_pages(args.style, TEMPLATES_DIR, STATIC_DIR)
    sprint(f'↪ Created html/css templates @ {PYDIR}')




# ------------------------------------------------------------------------------------------
from . import NEW_NOTEBOOK_STR
BOARD_FILE_MD = None
BOARD_PAGE = ""
if args.board:
    try: 
        from nbconvert import HTMLExporter 
        has_nbconvert_package=True
    except:
        sprint(f'[!] Board will not be enabled since it requires nbconvert>=7.16.2 which is missing\n  ⇒ pip install nbconvert')
        has_nbconvert_package = False

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

if not BOARD_FILE_MD:   sprint(f'⚙ Board: Not Available')
else:                   sprint(f'⚙ Board: Is Available')

TEMPLATE_BOARD =        args.style['template_board']
ICON_BOARD =            args.style['icon_board']
CAPTION_BOARD =         args.style['board_'] 
def update_board(): 
    global BOARD_PAGE
    res = False
    if BOARD_FILE_MD:
        try: 
            page,_ = HTMLExporter(template_name=TEMPLATE_BOARD).from_file(BOARD_FILE_MD, {'metadata':{'name':f'{ICON_BOARD} {CAPTION_BOARD} | {args.topic}'}}) 
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
# LOGIN DATABASE - CSV
# ------------------------------------------------------------------------------------------
if not args.login: fexit(f'[!] login file was not provided!')    
LOGIN_XL_PATH = os.path.join( BASEDIR, args.login) 
if not os.path.isfile(LOGIN_XL_PATH): 
    from . access import build_new
    sprint(f'⇒ Creating new login file: {LOGIN_XL_PATH}')
    this_user, this_platform = build_new(LOGIN_XL_PATH)
    sprint(f'⇒ Created new login with user "{this_user}", name "{this_platform}" at file: {LOGIN_XL_PATH}')

# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# SUBMIT DATABASE - CSV
# ------------------------------------------------------------------------------------------
if not args.submit: SUBMIT_XL_PATH = None # fexit(f'[!] submission file was not provided!')    
else: SUBMIT_XL_PATH = os.path.join( BASEDIR, args.submit)
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
def read_logindb_from_disk():
    db_frame, res = READ_DB_FROM_DISK(LOGIN_XL_PATH, 1)
    if res: sprint(f'⇒ Loaded login file: {LOGIN_XL_PATH}')
    else: sprint(f'⇒ Failed reading login file: {LOGIN_XL_PATH}')
    return db_frame
def read_submitdb_from_disk():
    dbsub_frame = None
    if SUBMIT_XL_PATH: 
        dbsub_frame, ressub = READ_DB_FROM_DISK(SUBMIT_XL_PATH, 0)
        if ressub: sprint(f'⇒ Loaded submission file: {SUBMIT_XL_PATH}')
        else: sprint(f'⇒ Did not load submission file: [{SUBMIT_XL_PATH}] exists={os.path.exists(SUBMIT_XL_PATH)} isfile={os.path.isfile(SUBMIT_XL_PATH)}')
    return dbsub_frame
# ------------------------------------------------------------------------------------------
def write_logindb_to_disk(db_frame): # will change the order
    res = WRITE_DB_TO_DISK(LOGIN_XL_PATH, db_frame, LOGIN_ORD)
    if res: sprint(f'⇒ Persisted login file: {LOGIN_XL_PATH}')
    else:  sprint(f'⇒ PermissionError - {LOGIN_XL_PATH} might be open, close it first.')
    return res
def write_submitdb_to_disk(dbsub_frame, verbose=True): # will change the order
    ressub = True
    if SUBMIT_XL_PATH: 
        ressub = WRITE_DB_TO_DISK(SUBMIT_XL_PATH, dbsub_frame, SUBMIT_ORD)
        if verbose:
            if ressub: sprint(f'⇒ Persisted submission file: {SUBMIT_XL_PATH}')
            else:  sprint(f'⇒ PermissionError - {SUBMIT_XL_PATH} might be open, close it first.')
    return ressub
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
db =    read_logindb_from_disk()  #<----------- Created database here 
dbsub = read_submitdb_from_disk()  #<----------- Created database here 
sprint('↷ persisted submit-db [{}]'.format(write_submitdb_to_disk(dbsub)))

# = { k : [vu,  vn, 0.0, ''] for k,(va,vu,vn,_) in db.items() if '-' not in va} 
# -----------------------------------------------------------------------------------------
#print(dbsub)
def GetUserFiles(uid): 
    if not REQUIRED_FILES: return True # no files are required to be uploaded
    udir = os.path.join( app.config['uploads'], uid)
    has_udir = os.path.isdir(udir)
    if has_udir: return not (False in [os.path.isfile(os.path.join(udir, f)) for f in REQUIRED_FILES])
    else: return False
 # The upload form using FlaskForm
class UploadFileForm(FlaskForm): file, submit = MultipleFileField("File", validators=[InputRequired()]), SubmitField("Upload File")

# ------------------------------------------------------------------------------------------
# application setting and instance
# ------------------------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key =          APP_SECRET_KEY
app.config['base'] =      BASEDIR
app.config['uploads'] =   UPLOAD_FOLDER_PATH
app.config['reports'] =   REPORT_FOLDER_PATH
app.config['downloads'] = DOWNLOAD_FOLDER_PATH
app.config['archives'] =  ARCHIVE_FOLDER_PATH
app.config['emoji'] =     args.emoji
app.config['topic'] =     args.topic
app.config['dfl'] =       GET_FILE_LIST(DOWNLOAD_FOLDER_PATH)
app.config['afl'] =       GET_FILE_LIST(ARCHIVE_FOLDER_PATH)
app.config['rename'] =    int(args.rename)
app.config['muc'] =       MAX_UPLOAD_COUNT
app.config['board'] =     (BOARD_FILE_MD is not None)
app.config['reg'] =       (parsed.reg)
# ------------------------------------------------------------------------------------------

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
                        msg=f'[{in_uid}] New password is invalid - can use alpha-numeric, underscore and @-symbol'
                        
                                               
                else: #new password not provided                
                    warn = LOGIN_NEW_TEXT
                    msg = f'[{in_uid}] New password required - can use alpha-numeric, underscore and @-symbol'
                                           
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
                            msg=f'[{in_uid}] New password is invalid - can use alpha-numeric, underscore and @-symbol'
                            
                                                
                    else: #new password not provided                  
                        warn = LOGIN_NEW_TEXT
                        msg = f'[{in_uid}] New password required - can use alpha-numeric, underscore and @-symbol'
                                            

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
# archive
# ------------------------------------------------------------------------------------------
@app.route('/archives', methods =['GET'], defaults={'req_path': ''})
@app.route('/archives/<path:req_path>')
def route_archives(req_path):
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if not 'A' in session['admind']: return redirect(url_for('route_home'))
    abs_path = os.path.join(app.config['archives'], req_path) # Joining the base and the requested path
    if not os.path.exists(abs_path): 
        dprint(f"⇒ requested file was not found {abs_path}") #Return 404 if path doesn't exist
        return abort(404) 
    if os.path.isfile(abs_path):  #(f"◦ sending file ")
        dprint(f'● {session["uid"]} ◦ {session["named"]} just downloaded the file {req_path} via {request.remote_addr}')
        return send_file(abs_path) # Check if path is a file and serve
    return render_template('archives.html')
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

@app.route('/submit', methods =['GET', 'POST'])
def route_submit():
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    if request.method == 'POST': 
        global db, dbsub #, HAS_PENDING
        submitter = session['uid']
        if 'resetpass' in request.form:
            if ('X' in session['admind']) or ('+' in session['admind']):
                in_uid = f"{request.form['resetpass']}"
                if in_uid: 
                    in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
                    record = db.get(in_query, None)
                    if record is not None: 
                        admind, uid, named, _ = record
                        if (('X' not in admind) and ('+' not in admind)) or (submitter==uid):
                            db[uid][3]='' ## 3 for PASS  record['PASS'].values[0]=''
                            #HAS_PENDING+=1
                            dprint(f"▶ {submitter} ◦ {session['named']} just reset the password for {uid} ◦ {named} via {request.remote_addr}")
                            status, success =  f"Password was reset for {uid} {named}.", True
                        else: status, success =  f"You cannot reset password for account '{in_query}'.", False
                    else: status, success =  f"User '{in_query}' not found.", False
                else: status, success =  f"User-id was not provided.", False
            else: status, success =  "You are not allow to reset passwords.", False

        elif 'uid' in request.form and 'score' in request.form:
            if SUBMIT_XL_PATH:
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
                                    #if scored[-1] == submitter or ('+' in session['admind']):
                                    if in_score:  dbsub[in_query][2] = in_score
                                    if in_remark: dbsub[in_query][3] = in_remark
                                    if in_score or in_remark : status, success =    f'Score/Remark Updated for [{in_uid}] {named}, current score is {dbsub[in_query][2]}. Remark is [{dbsub[in_query][3]}].', True
                                    #else: status, success =                         f'Nothing was updated for [{in_uid}] {named}, current score is {dbsub[in_query][2]}. Remark is [{dbsub[in_query][3]}].', False
                                    upby = f' [forced from {scored[-1]}]' if scored[-1] == submitter else ''
                                    dprint(f"▶ {submitter} ◦ {session['named']} updated{upby} the evaluation for {uid} ◦ {named} via {request.remote_addr}")

                                    # (already evaluated by [{scored[-1]}]) 
                                    #else:
                                    #status, success = f'[{in_uid}] {named} has been evaluated by [{scored[-1]}], you cannot update the information.', False
                                    
                
                else: status, success =  "You are not allow to evaluate.", False
            else: status, success =  "Evaluation is disabled.", False
        else: status, success = f"You posted nothing!", False
        
        if success: persist_subdb()
        
    else:
        if ('+' in session['admind']) or ('X' in session['admind']):
            status, success = f"Eval Access is Enabled", True
        else: status, success = f"Eval Access is Disabled", False
    
    return render_template('submit.html', success=success, status=status)



# ------------------------------------------------------------------------------------------
# home - upload
# ------------------------------------------------------------------------------------------


@app.route('/home', methods =['GET', 'POST'])
def route_home():
    if not session.get('has_login', False): return redirect(url_for('route_login'))
    form = UploadFileForm()
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    if SUBMIT_XL_PATH:
        submitted = int(session['uid'] in dbsub)
        score = dbsub[session['uid']][2] if submitted>0 else -1
    else: submitted, score = -1, -1

    if form.validate_on_submit() and ('U' in session['admind']):
        dprint(f"● {session['uid']} ◦ {session['named']} is trying to upload {len(form.file.data)} items via {request.remote_addr}")
        if app.config['muc']==0: 
            return render_template('home.html', submitted=submitted, score=score, form=form, status=[(0, f'✗ Uploads are disabled')])
        
        if SUBMIT_XL_PATH:
            if submitted>0: return render_template('home.html', submitted=submitted, score=score, form=form, status=[(0, f'✗ You have been evaluated - cannot upload new files for this session.')])

        result = []
        n_success = 0
        #---------------------------------------------------------------------------------
        for file in form.file.data:
            isvalid, sf = VALIDATE_FILENAME(secure_filename(file.filename))
        #---------------------------------------------------------------------------------
            
            if not isvalid:
                why_failed =  f"✗ File not accepted [{sf}] " if REQUIRED_FILES else f"✗ Extension is invalid [{sf}] "
                result.append((0, why_failed))
                continue

            file_name = os.path.join(folder_name, sf)
            if not os.path.exists(file_name):
                #file_list = os.listdir(folder_name)
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
    
    #file_list = session['filed'] #os.listdir(folder_name)
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
# if not '-' in session['admind']:        return redirect(url_for('route_home'))
# global dbsub
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
    if SUBMIT_XL_PATH:
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
            elif in_cmd=="ref_archives": STATUS, SUCCESS = update_al()
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

def update_al():
    r""" refreshes the  downloads"""
    app.config['afl'] = GET_FILE_LIST(ARCHIVE_FOLDER_PATH)
    dprint(f"▶ {session['uid']} ◦ {session['named']} just refreshed the archive list via {request.remote_addr}")
    return "Updated archive-list", True #  STATUS, SUCCESS

def persist_db():
    r""" writes both dbs to disk """
    global db, dbsub
    if write_logindb_to_disk(db) and write_submitdb_to_disk(dbsub): #if write_db_to_disk(db, dbsub):
        dprint(f"▶ {session['uid']} ◦ {session['named']} just persisted the db to disk via {request.remote_addr}")
        STATUS, SUCCESS = "Persisted db to disk", True
    else: STATUS, SUCCESS =  f"Write error, file might be open", False
    return STATUS, SUCCESS 

def persist_subdb():
    r""" writes submit-db to disk """
    global dbsub
    if write_submitdb_to_disk(dbsub, verbose=False): 
        #dprint(f"▶ {session['uid']} ◦ {session['named']} just persisted the submit-db to disk via {request.remote_addr}")
        STATUS, SUCCESS = "Persisted db to disk", True
    else: STATUS, SUCCESS =  f"Write error, file might be open", False
    return STATUS, SUCCESS 

def reload_db():
    r""" reloads db from disk """
    global db, dbsub#, HAS_PENDING
    db = read_logindb_from_disk()
    dbsub = read_submitdb_from_disk()
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
    return render_template('admin.html',  status=STATUS, success=SUCCESS)
# ------------------------------------------------------------------------------------------




# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#<-------------------DO NOT WRITE ANY NEW CODE AFTER THIS
def endpoints(athost):
    if athost=='0.0.0.0':
        import socket
        ips=set()
        for info in socket.getaddrinfo(socket.gethostname(), None):
            if (info[0].name == socket.AddressFamily.AF_INET.name): ips.add(info[4][0])
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
    #_quiet=True,
)
#<-------------------DO NOT WRITE ANY CODE AFTER THIS
end_time = datetime.datetime.now()
sprint('◉ stop server @ [{}]'.format(end_time))
sprint('↷ persisted login-db [{}]'.format(write_logindb_to_disk(db)))
sprint('↷ persisted submit-db [{}]'.format(write_submitdb_to_disk(dbsub)))

if bool(parsed.coe):
    sprint(f'↪ Cleaning up html/css templates...')
    try:
        for k,v in HTML_TEMPLATES.items():
            h = os.path.join(TEMPLATES_DIR, f"{k}.html")
            if  os.path.isfile(h) : os.remove(h)
        #sprint(f'↪ Removing css templates @ {STATIC_DIR}')
        for k,v in CSS_TEMPLATES.items():
            h = os.path.join(STATIC_DIR, f"{k}.css")
            if os.path.isfile(h): os.remove(h)
        os.removedirs(TEMPLATES_DIR)
        os.removedirs(STATIC_DIR)
        sprint(f'↪ Removed html/css templates @ {PYDIR}')
    except:
        sprint(f'↪ Could not remove html/css templates @ {PYDIR}')
sprint('◉ server up-time was [{}]'.format(end_time - start_time))
sprint(f'...Finished!')
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@