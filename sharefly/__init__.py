
__doc__=f""" 
-------------------------------------------------------------
ShareFly - Flask-based web app for sharing files 
-------------------------------------------------------------
"""
def DEFAULT_CONFIG(file_path):
    with open(file_path, 'w', encoding='utf-8') as f: f.write("""

def merged(a:dict, b:dict): return {**a, **b}

default = dict(    

    # -------------------------------------# general info
    topic        = "ShareFly",             # topic text (main banner text)
    welcome      = "Login to Continue",    # msg shown on login page
    register     = "Register User",        # msg shown on register (new-user) page
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
    base         = "__base__",            # the base directory 
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
                        logout_=        'Logout',
                        login_=         'Login',
                        new_=           'Register',
                        eval_=          'Eval',
                        resetpass_=     'Reset',
                        report_=        'Report',

                        # -------------# colors 
                        bgcolor      = "white",
                        fgcolor      = "black",
                        refcolor     = "#232323",
                        item_bgcolor = "#232323",
                        item_normal  = "#e6e6e6",
                        item_true    = "#47ff6f",
                        item_false   = "#ff6565",
                        flup_bgcolor = "#ebebeb",
                        flup_fgcolor = "#232323",
                        fldown_bgcolor = "#ebebeb",
                        fldown_fgcolor = "#232323",
                        msgcolor =     "#060472",
                        
                        # -------------# icons 
                        icon_board =    '🔰',
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

                        # -------------# board style ('lab'  'classic' 'reveal')
                        template_board = 'lab', 
                    )
    )

""")

def FAVICON(favicon_path):
    with open( favicon_path, 'wb') as f: f.write((b''.join([i.to_bytes() for i in [
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
    ]])))

def TEMPLATES(style):

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
            <button class="btn_purge_large" onclick="confirm_repass()">"""+'Reset Password' + """</button>
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
            <a href="{{ url_for('route_generate_eval_template') }}" class="btn_black">Get CSV-Template</a>
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
    # ****************************************************************************************** 
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
    .btn_black {
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
    return HTML_TEMPLATES, CSS_TEMPLATES
    # ****************************************************************************************** 


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# author: Nelson.S
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@