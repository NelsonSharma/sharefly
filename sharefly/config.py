

def merged(a:dict, b:dict): return {**a, **b}

# specified by --configd arg
default = dict(    

    # -------------------------------------# general info
    topic        = "ShareFly",             # topic text (main banner text)
    welcome      = "Welcome!",             # msg shown on login page
    register     = "Register!",            # msg shown on register (new-user) page
    emoji        = "◉",                    # emoji shown of login page and seperates uid - name
    rename       = 0,                      # if rename=1, allows users to update their names when logging in
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
    port         = "8080",                 # port
    host         = "0.0.0.0",              # ip

    # ------------------------------------# file and directory information
    base 		 = "__base__",            # the base directory 
    login        = "__login__.csv",       # login database
    submit       = "__submit__.csv",      # submission database - created if not existing - reloads if exists
    uploads      = "__uploads__",         # uploads folder (uploaded files by users go here)
    reports      = "__reports__",         # reports folder (personal user access files by users go here)
    downloads    = "__downloads__",       # downloads folder
    board        = "__board__.ipynb",     # board file

    # --------------------------------------# style dict
    style        = dict(                   
                        # -------------# labels
                        downloads_ =    'Downloads',
                        uploads_ =      'Uploads',
                        board_=         'Board',
                        admin_=         'Admin',
                        logout_=        'Logout',
                        login_=         'Login',
                        new_=           'Register',
                        submit_=        'Eval',
                        resetpass_=     'Reset',
                        report_=        'Report',

                        # -------------# icons 
                        icon_board =    '🔰',
                        icon_admin=     '⭐',
                        icon_login=     '🔒',
                        icon_new=       '👤',
                        icon_home=      '🔘',
                        icon_downloads= '📥',
                        icon_uploads=   '📤',
                        icon_submit=    '✴️',
                        icon_report=    '📜',

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
