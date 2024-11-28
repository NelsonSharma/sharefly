
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
137,80,78,71,13,10,26,10,0,0,0,13,73,72,68,82,0,0,0,32,0,0,0,32,8,6,0,0,1,4,125,74,98,0,0,0,9,112,72,89,
115,0,0,13,214,0,0,13,214,1,144,111,121,156,0,0,9,130,73,68,65,84,88,9,205,87,121,84,148,215,21,255,125,223,236,48,44,195,190,202,
166,17,84,20,149,40,46,71,69,196,163,104,84,2,99,92,18,143,113,1,219,186,212,86,49,61,193,35,86,115,76,76,172,75,244,52,154,26,27,143,
165,169,40,42,46,168,32,166,41,46,36,106,100,81,81,65,20,144,69,97,128,97,96,54,102,190,222,247,17,60,68,123,98,19,251,71,223,57,223,188,
247,238,187,247,190,123,223,93,135,19,4,1,63,26,147,39,107,15,9,159,105,69,232,142,37,90,129,99,167,191,155,163,21,74,155,129,37,3,0,158,
1,18,135,58,224,252,76,204,59,89,195,131,123,158,7,183,121,65,178,96,244,234,235,125,241,122,69,156,74,194,101,242,183,90,57,8,117,149,141,137,
33,200,180,1,115,248,167,70,148,172,91,18,12,169,143,11,36,28,46,128,174,77,160,239,239,140,249,111,82,87,250,253,48,15,101,51,193,191,21,197,
152,53,227,45,33,115,77,16,150,125,242,0,106,31,95,157,167,131,193,109,109,162,39,18,50,30,64,68,16,206,164,8,48,11,248,254,161,21,31,93,
225,17,166,54,34,58,64,138,71,45,246,23,197,100,172,123,143,23,244,232,125,200,214,28,9,82,66,243,148,243,231,179,234,122,31,18,124,41,237,181,
82,171,13,145,9,65,120,236,52,77,107,246,9,240,125,157,128,185,139,189,235,253,219,173,192,7,215,233,237,56,18,115,209,252,96,124,152,18,168,168,
174,107,94,241,184,186,206,63,116,66,48,52,81,254,32,75,100,136,90,228,175,211,10,5,53,2,42,244,28,252,213,64,113,19,144,66,47,63,103,87,
22,39,29,57,46,57,253,111,15,120,4,186,240,24,27,226,128,226,7,70,228,46,117,128,201,218,109,72,190,232,155,35,155,83,98,84,80,73,129,141,
39,90,250,234,141,246,78,185,146,195,145,98,179,40,243,203,213,124,222,158,189,85,253,111,214,236,157,26,9,209,203,70,34,49,141,104,46,185,152,159,
53,132,12,91,179,103,239,174,64,198,132,214,131,105,106,43,171,168,247,151,241,184,196,19,34,211,128,225,115,19,226,146,71,31,91,224,114,201,213,149,
199,173,234,46,252,225,140,1,31,143,6,126,91,136,218,190,33,126,86,146,112,74,125,147,62,40,45,188,227,124,246,3,192,199,67,142,149,99,85,144,
168,56,204,218,219,102,23,159,145,164,144,218,5,172,148,66,216,54,187,47,240,117,163,4,73,147,60,240,233,177,39,226,45,51,71,185,162,86,103,133,
188,197,0,165,132,44,85,45,220,81,201,249,21,100,221,11,162,147,19,151,137,114,30,219,166,71,42,33,168,149,248,242,29,103,60,190,223,10,57,33,
59,209,254,82,137,30,91,98,101,216,152,164,65,133,81,138,190,30,210,8,82,53,159,52,232,142,18,186,230,126,27,185,99,106,140,146,193,96,178,8,
40,215,243,48,219,81,190,106,16,254,146,62,207,23,167,74,77,248,213,225,118,236,159,235,132,112,47,9,147,172,157,225,138,42,176,5,27,147,226,181,
57,179,6,41,222,184,219,198,161,170,193,92,127,234,204,97,49,66,198,142,79,10,94,63,215,167,234,224,185,167,232,32,31,235,180,8,33,36,254,67,
70,243,82,59,51,164,159,26,175,204,64,124,196,159,186,225,101,103,204,145,206,19,146,43,125,159,147,94,159,51,2,114,156,97,228,68,55,216,154,13,
150,45,104,47,6,36,225,179,119,217,70,223,64,250,222,99,18,196,147,87,177,64,220,71,143,40,140,143,211,146,27,161,153,136,34,105,238,25,223,178,
69,236,36,109,49,249,203,99,50,225,28,218,178,243,3,162,10,118,59,240,254,112,96,122,16,176,125,12,46,125,127,175,142,49,201,165,143,221,30,233,
234,228,48,52,105,154,214,84,144,140,193,83,200,185,99,125,5,80,38,96,35,143,155,57,109,182,237,120,170,11,111,51,10,216,85,104,68,67,147,5,
111,134,2,91,203,29,227,125,61,156,171,57,142,59,91,81,85,39,219,49,22,1,107,47,3,91,18,212,24,216,71,138,214,86,59,18,15,182,141,225,
226,227,181,25,230,46,97,195,238,101,1,8,245,145,163,139,228,219,158,211,132,226,187,237,240,11,244,109,169,169,215,29,209,112,230,165,235,23,247,129,
191,70,10,35,37,130,197,59,171,161,239,180,163,32,63,139,101,28,49,133,198,25,45,194,167,83,251,32,194,68,162,89,52,106,4,184,201,112,226,74,
171,24,117,43,18,189,112,52,191,9,19,188,109,56,92,1,116,129,251,61,69,228,46,122,244,46,241,13,44,118,120,46,31,194,69,132,105,56,20,54,
114,240,232,52,160,242,94,43,227,13,55,5,80,84,248,4,1,74,27,202,90,56,172,25,198,193,83,133,109,140,152,157,83,184,0,97,97,3,75,159,
90,120,84,24,120,100,47,114,193,232,126,42,124,121,195,2,137,66,65,110,219,133,232,96,5,214,37,56,161,86,47,160,193,42,69,89,131,13,161,97,
3,175,84,86,222,174,20,37,152,30,46,199,142,89,106,188,17,33,131,133,116,124,255,180,1,14,42,9,100,50,25,166,70,59,35,134,30,109,3,193,
22,143,86,225,122,173,21,167,87,105,208,106,18,152,233,65,169,16,56,93,110,105,183,218,5,167,181,113,142,98,196,77,11,151,33,116,128,59,154,74,
155,247,255,177,200,52,230,126,160,50,252,195,120,71,124,113,217,136,125,90,39,140,221,170,131,171,138,203,100,180,162,4,228,72,161,238,14,60,222,57,
164,199,159,41,92,43,44,114,100,100,54,116,142,243,54,21,220,172,179,77,223,52,223,7,59,191,238,192,107,30,18,92,171,233,130,74,198,149,156,59,
151,85,197,24,60,11,103,114,209,96,7,57,87,229,40,3,22,76,246,196,166,175,26,66,10,255,121,244,33,67,154,158,48,187,46,196,71,225,219,223,
69,192,241,50,243,201,252,188,172,25,12,206,198,255,65,52,190,106,93,232,86,228,151,255,138,70,248,229,228,175,78,249,172,176,253,7,86,13,4,99,
249,105,59,121,125,11,59,167,204,240,49,77,1,148,155,230,178,253,243,131,206,191,34,88,53,157,167,177,51,114,12,13,77,171,233,99,205,132,15,125,
207,143,39,76,128,171,4,29,73,174,8,42,77,88,77,53,52,196,5,216,124,13,24,238,1,4,57,147,20,183,209,166,51,35,181,176,32,235,31,116,
201,78,66,245,164,75,230,245,230,70,112,214,106,61,33,248,170,177,19,181,111,81,8,239,93,58,0,46,15,245,192,13,106,55,210,163,129,170,54,210,
134,250,29,10,253,30,247,45,146,80,24,187,216,236,152,60,33,76,134,133,35,84,168,54,73,144,243,16,104,234,16,112,91,7,76,165,252,183,54,26,
202,81,94,72,126,236,48,48,173,188,182,53,189,143,143,198,39,122,248,136,133,223,93,47,202,102,66,208,229,153,18,158,175,41,42,171,206,25,49,40,
242,206,142,49,152,187,34,10,74,93,39,176,191,156,16,40,103,221,235,148,66,237,42,199,172,72,5,236,148,176,30,232,236,212,61,97,59,23,51,62,
217,81,163,226,110,46,139,81,245,149,208,11,176,64,171,211,219,33,16,145,132,50,141,158,234,109,43,229,90,144,148,211,3,5,216,9,158,93,41,156,
13,15,243,173,226,121,78,205,216,219,237,66,123,121,101,125,72,82,24,55,133,226,10,167,106,40,60,137,25,69,59,156,21,28,108,116,33,131,251,57,
243,136,166,180,194,246,159,93,53,86,180,24,133,168,158,116,74,143,142,131,132,51,67,37,231,196,252,163,32,123,80,138,133,92,198,33,192,93,142,33,
33,74,248,122,202,112,250,106,27,246,229,54,179,226,111,146,203,152,200,244,164,86,155,93,41,231,148,41,83,221,49,45,198,5,245,79,173,40,174,50,
161,182,217,34,230,54,198,211,76,239,158,123,77,47,242,36,29,114,136,108,1,249,22,117,0,207,141,137,147,180,105,86,59,50,2,212,80,69,145,15,
244,33,29,163,220,1,15,21,112,189,81,192,181,39,84,240,172,28,234,58,0,157,169,155,216,141,26,18,63,71,192,93,38,32,218,139,124,199,155,67,
147,17,184,217,76,30,105,160,153,124,160,214,0,35,117,102,25,84,68,182,246,190,242,153,0,228,140,78,102,27,190,75,29,128,254,163,124,1,214,179,
150,234,136,145,153,131,143,139,4,254,212,189,5,208,236,229,196,227,236,29,11,174,62,178,66,202,51,215,165,2,67,61,90,76,144,12,83,34,228,120,
210,110,71,109,155,13,143,169,228,53,208,236,161,16,16,233,38,96,98,32,135,43,245,192,222,219,184,171,144,224,117,210,94,108,141,196,108,222,205,4,
169,222,142,92,127,141,151,18,158,161,114,140,215,216,112,49,175,19,159,204,112,132,55,245,199,102,106,137,62,42,232,68,209,35,1,228,51,232,231,43,
135,141,119,16,5,144,216,59,161,150,11,56,89,102,134,19,217,252,189,137,14,100,58,160,177,205,142,53,167,58,48,126,176,3,60,53,18,184,218,44,
240,126,100,234,223,212,41,164,16,33,107,45,126,104,238,104,65,237,66,35,79,22,109,37,167,75,59,97,192,137,219,22,28,156,231,4,79,210,120,11,
9,178,62,183,3,105,19,84,228,139,2,250,245,115,134,171,154,239,50,152,113,183,221,140,114,13,173,25,140,157,49,156,116,194,101,52,140,150,241,56,
113,203,34,242,100,13,36,187,131,221,197,46,103,227,153,9,216,134,250,154,61,84,106,126,125,96,182,26,238,110,18,92,46,183,96,55,213,176,63,205,
84,83,171,202,97,249,49,3,54,188,237,135,139,37,6,236,202,109,222,124,251,93,9,121,6,132,1,7,108,166,149,83,221,211,99,7,171,177,241,80,
29,118,39,170,97,233,18,176,58,199,128,21,84,68,71,83,193,109,214,217,240,238,97,114,4,171,176,135,170,209,114,118,31,27,63,18,128,1,168,75,
137,232,178,227,56,53,39,175,69,249,74,176,115,182,19,110,84,90,177,179,200,130,189,203,3,113,168,64,135,191,94,208,125,113,233,155,163,139,25,126,
207,24,51,46,105,255,194,73,110,139,222,142,117,67,234,238,26,172,26,41,199,48,202,45,171,168,37,190,89,111,99,127,14,239,73,121,204,202,203,203,
186,211,67,195,230,23,4,232,57,156,255,166,150,171,215,99,50,181,76,137,74,41,23,73,73,195,153,90,38,29,81,164,95,188,112,228,95,61,120,189,
231,216,184,228,113,212,6,109,146,74,56,55,122,102,189,169,75,40,85,72,185,108,63,103,228,29,202,206,234,246,216,222,4,180,126,229,122,252,28,191,
159,189,21,19,201,207,166,250,31,18,252,27,83,9,228,212,162,170,157,114,0,0,0,0,73,69,78,68,174,66,96,130,
]
])))

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