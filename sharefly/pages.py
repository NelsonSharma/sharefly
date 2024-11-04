# ------------------------------------------------------------------------------------------
# html pages
# ------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
# Create HTML
# ------------------------------------------------------------------------------------------

import os
def make_pages(style, TEMPLATES_DIR, STATIC_DIR):
    #style = getattr(args, 'style')
    PAGES_HTML = HTML_TEMPLATES(
        CAPTION_DOWNLOADS =     style['downloads_'],
        CAPTION_UPLOADS =       style['uploads_'] ,
        CAPTION_ARCHIVES =      style['archives_'] , 
        CAPTION_BOARD =         style['board_'] ,
        CAPTION_ADMIN =         style['admin_'] ,
        CAPTION_LOGOUT =        style['logout_'] ,
        CAPTION_LOGIN =         style['login_'] ,
        CAPTION_NEW =           style['new_'] ,
        CAPTION_SUBMIT =        style['submit_'], 
        CAPTION_RESET_PASS =    style['resetpass_'], 
        CAPTION_REPORT =        style['report_'] ,

        ICON_BOARD =            style['icon_board'], 
        ICON_ADMIN =            style['icon_admin'] ,
        ICON_LOGIN =            style['icon_login'] ,
        ICON_NEW =              style['icon_new'] ,
        ICON_HOME =             style['icon_home'] ,
        ICON_DOWNLOADS =        style['icon_downloads'] ,
        ICON_UPLOADS =          style['icon_uploads'] ,
        ICON_ARCHIVES =         style['icon_archives'] ,
        ICON_SUBMIT =           style['icon_submit'] ,
        ICON_REPORT =           style['icon_report'] ,

        AA_REFD=                style['aa_ref_downloads'], 
        AA_REFA=                style['aa_ref_archives'],
        AA_DBW=                 style['aa_db_write'],
        AA_DBR=                 style['aa_db_read'],
        AA_REFB=                style['aa_ref_board'],
        AA_RESETPASS=           style['aa_reset_pass'],


        TEMPLATE_BOARD =        style['template_board'], 
    )


    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    #sprint(f'↪ Creating html templates @ {TEMPLATES_DIR}')
    for k,v in PAGES_HTML.items():
        h = os.path.join(TEMPLATES_DIR, f"{k}.html")
        if (not os.path.isfile(h)):
            #sprint(f'  ↦ page:{h}')
            with open(h, 'w', encoding='utf-8') as f: f.write(v)

    os.makedirs(STATIC_DIR, exist_ok=True)
    #sprint(f'↪ Creating css templates @ {STATIC_DIR}')
    for k,v in CSS_TEMPLATES.items():
        h = os.path.join(STATIC_DIR, f"{k}.css")
        if (not os.path.isfile(h)):
            #sprint(f'  ↦ page:{h}')
            with open(h, 'w', encoding='utf-8') as f: f.write(v)



# ******************************************************************************************
def HTML_TEMPLATES(
    CAPTION_DOWNLOADS,
    CAPTION_UPLOADS,
    CAPTION_ARCHIVES,
    CAPTION_BOARD,
    CAPTION_ADMIN,
    CAPTION_LOGOUT,
    CAPTION_LOGIN,
    CAPTION_NEW,
    CAPTION_SUBMIT,
    CAPTION_RESET_PASS,
    CAPTION_REPORT,

    ICON_BOARD,
    ICON_ADMIN, 
    ICON_LOGIN, 
    ICON_NEW,
    ICON_HOME,
    ICON_DOWNLOADS, 
    ICON_UPLOADS,
    ICON_ARCHIVES,
    ICON_SUBMIT,
    ICON_REPORT, 

    AA_REFD,
    AA_REFA,
    AA_DBW,
    AA_DBR,
    AA_REFB,
    AA_RESETPASS,

    TEMPLATE_BOARD,
): return dict(
# ******************************************************************************************
board="""""",
# ******************************************************************************************
submit = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{ICON_SUBMIT}'+""" {{ config.topic }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">  
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->

    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{CAPTION_LOGOUT}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_back">Back</a>
        <a href="{{ url_for('route_submit') }}" class="btn_refresh">Refresh</a>
        <br>
        <br>
        {% if success %}
        <span class="admin_mid" style="animation-name: fader_admin_success;">✓ {{ status }} </span>
        {% else %}
        <span class="admin_mid" style="animation-name: fader_admin_failed;">✗ {{ status }} </span>
        {% endif %}
        <br>

        
        <br>

        <form action="{{ url_for('route_submit') }}" method="post">
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
        </form>
        <br>
        <br>
        <form action="{{ url_for('route_submit') }}" method="post">
            <input id="resetpass" name="resetpass" type="text" style="width:100px;color: #9a0808; background: rgb(255, 171, 171)" placeholder="uid" class="txt_submit"/>
            <input type="submit" class="btn_purge_large" value="Reset Password"> 
        </form>        
    </div>

            
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
        <title> """+f'{ICON_ADMIN}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">					 
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{CAPTION_LOGOUT}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_back">Back</a>
        <a href="{{ url_for('route_adminpage') }}" class="btn_refresh">Refresh</a>
        <br>
        <br>
        {% if success %}
        <span class="admin_mid" style="animation-name: fader_admin_success;">✓ {{ status }} </span>
        {% else %}
        <span class="admin_mid" style="animation-name: fader_admin_failed;">✗ {{ status }} </span>
        {% endif %}
        <br>
        <br>
        {% if '+' in session.admind %}
        <a href="{{ url_for('route_adminpage',req_cmd='ref_downloads') }}" class="btn_admin_actions">"""+f'{AA_REFD}'+"""<span class="tooltiptext">Refresh Downloads</span></a> <!--Update download-list --!>
        <a href="{{ url_for('route_adminpage',req_cmd='ref_archives') }}" class="btn_admin_actions">"""+f'{AA_REFA}'+"""<span class="tooltiptext">Refresh Archives</span></a> <!--Update archive-list --!>
        <a href="{{ url_for('route_adminpage',req_cmd='db_write') }}" class="btn_admin_actions">"""+f'{AA_DBW}'+"""<span class="tooltiptext">Persist Database</span></a> <!--Persist login-database --!>
        <a href="{{ url_for('route_adminpage',req_cmd='db_read') }}" class="btn_admin_actions">"""+f'{AA_DBR}'+"""<span class="tooltiptext">Reload Database</span></a> <!--Reload login-database --!>
        <a href="{{ url_for('route_adminpage',req_cmd='ref_board') }}" class="btn_admin_actions">"""+f'{AA_REFB}'+"""<span class="tooltiptext">Refresh Board</span></a> <!--Refresh board --!>
        <button class="btn_admin_actions" onclick="confirm_repass()">"""+f'{AA_RESETPASS}'+"""<span class="tooltiptext">Reset Password</span></button>
        
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
        <title> """+f'{ICON_LOGIN}'+""" {{ config.topic }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">  
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
            <input type="submit" class="btn_login" value=""" +f'"{CAPTION_LOGIN}"'+ """> 
            <br>
            <br>
        </form>
    </div>

    <!-- ---------------------------------------------------------->
    
    <div align="center">
    <div>
    <span style="font-size: xx-large;">{{ config.emoji }}</span>
    <br>
    {% if config.reg %}
    <a href="{{ url_for('route_new') }}" class="btn_board">""" + f'{CAPTION_NEW}' +"""</a>
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
        <title> """+f'{ICON_NEW}'+""" {{ config.topic }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">  
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
            <input type="submit" class="btn_board" value=""" + f'"{CAPTION_NEW}"' +"""> 
            <br>
            <br>
            
        </form>
    </div>

    <!-- ---------------------------------------------------------->
    
    <div align="center">
    <div>
    <span style="font-size: xx-large;">{{ config.emoji }}</span>
    <br>
    <a href="{{ url_for('route_login') }}" class="btn_login">""" + f'{CAPTION_LOGIN}' +"""</a>
    
    </div>
    <!-- <a href="https://emojipicker.com/" target="_blank" class="btn_login">...</a> -->
    <!--<div style="font-size:large"><a href="https://github.com/NelsonSharma/topics"  target="_blank"> 📤 📥 </a></div>-->
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
        <title> """+f'{ICON_DOWNLOADS}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">           
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{CAPTION_LOGOUT}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_back">Back</a>
        <br>
        <br>
        <div class="files_status">"""+f'{CAPTION_DOWNLOADS}'+"""</div>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in config.dfl %}
            <li><a href="{{ (request.path + '/' if request.path != '/' else '') + file }}" style="text-decoration: none; color: rgb(20, 20, 20);" >{{ file }}</a></li>
            <br>
            {% endfor %}
            </ol>
        </div>
        <br>
        <br>
    </div>

    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
archives = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> """+f'{ICON_ARCHIVES}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">           
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{CAPTION_LOGOUT}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_back">Back</a>
        <br>
        <br>
        <div class="files_status">"""+f'{CAPTION_ARCHIVES}'+"""</div>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in config.afl %}
            <li><a href="{{ (request.path + '/' if request.path != '/' else '') + file }}" style="text-decoration: none; color: rgb(20, 20, 20);" >{{ file }}</a></li>
            <br>
            {% endfor %}
            </ol>
        </div>
        <br>
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
        <title> """+f'{ICON_UPLOADS}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">           
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{CAPTION_LOGOUT}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_back">Back</a>
        <br>
        <br>
        <div class="files_status">"""+f'{CAPTION_UPLOADS}'+"""</div>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in session.filed %}
            <li><a href="{{ (request.path + '/' if request.path != '/' else '') + file }}" style="text-decoration: none; color: rgb(20, 20, 20);" >{{ file }}</a></li>
            <br>
            {% endfor %}
            </ol>
        </div>
        <br>
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
        <title> """+f'{ICON_REPORT}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">           
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{CAPTION_LOGOUT}'+"""</a>
        <a href="{{ url_for('route_home') }}" class="btn_back">Back</a>
        <br>
        <br>
        <div class="files_status">"""+f'{CAPTION_REPORT}'+"""</div>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in session.reported %}
            <li><a href="{{ (request.path + '/' if request.path != '/' else '') + file }}"  target="_blank" style="text-decoration: none; color: rgb(20, 20, 20);" >{{ file }}</a></li>
            <br>
            {% endfor %}
            </ol>
        </div>
        <br>
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
        <title> """+f'{ICON_HOME}'+""" {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">					 
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('route_logout') }}" class="btn_logout">"""+f'{CAPTION_LOGOUT}'+"""</a>
        {% if "S" in session.admind %}
        <a href="{{ url_for('route_uploads') }}" class="btn_upload">"""+f'{CAPTION_UPLOADS}'+"""</a>
        {% endif %}
        {% if "D" in session.admind %}
        <a href="{{ url_for('route_downloads') }}" class="btn_download">"""+f'{CAPTION_DOWNLOADS}'+"""</a>
        {% endif %}
        {% if "A" in session.admind %}
        <a href="{{ url_for('route_archives') }}" class="btn_archive">"""+f'{CAPTION_ARCHIVES}'+"""</a>
        {% endif %}
        {% if "B" in session.admind and config.board %}
        <a href="{{ url_for('route_board') }}" class="btn_board" target="_blank">"""+f'{CAPTION_BOARD}'+"""</a>
        {% endif %}
        {% if 'X' in session.admind or '+' in session.admind %}
        <a href="{{ url_for('route_submit') }}" class="btn_submit">"""+f'{CAPTION_SUBMIT}'+"""</a>
        {% endif %}
        {% if 'R' in session.admind %}
        <a href="{{ url_for('route_reports') }}" class="btn_report">"""+f'{CAPTION_REPORT}'+"""</a>
        {% endif %}
        
        {% if '+' in session.admind %}
        <a href="{{ url_for('route_adminpage') }}" class="btn_admin">"""+f'{CAPTION_ADMIN}'+"""</a>
        {% endif %}
        <br>
        <br>
        {% if config.muc!=0 and "U" in session.admind %}
                <div class="status">
                    <ol>
                    {% for s,f in status %}
                    {% if s %}
                    {% if s<0 %}
                    <li style="color: #ffffff;">{{ f }}</li>
                    {% else %}
                    <li style="color: #47ff6f;">{{ f }}</li>
                    {% endif %}
                    {% else %}
                    <li style="color: #ff6565;">{{ f }}</li>
                    {% endif %}
                    {% endfor %}
                    </ol>
                </div>
                <br>
                {% if submitted<1 %}
                <form method='POST' enctype='multipart/form-data'>
                    {{form.hidden_tag()}}
                    {{form.file()}}
                    {{form.submit()}}
                </form>
                {% else %}
                <div class="upword">Your Score is <span style="color:seagreen;">{{ score }}</span>  </div>
                {% endif %}
                <br>
                
                <div> <span class="upword">Uploads</span> 
                
                {% if "U" in session.admind and submitted<1 %}
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
# ******************************************************************************************
)
# ******************************************************************************************
CSS_TEMPLATES = dict(
# ****************************************************************************************** 0b7daa
style = """

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


.github_info {
    padding: 2px 10px;
    background-color: #516fa7; 
    color: #ffffff;
    font-size: medium;
    font-weight: bold;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.topic{
    color: #000000;
    font-size: xxx-large;
    font-weight: bold;
    font-family:monospace;    
}


.msg_login{
    color: #060472; 
    font-size: large;
    font-weight: bold;
    font-family:monospace;    
    animation-duration: 3s; 
    animation-name: fader_msg;
}
@keyframes fader_msg {from {color: #ffffff;} to {color: #060472; } }


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

.topic_mid{
    color: #000000;
    font-size: x-large;
    font-style: italic;
    font-weight: bold;
    font-family:monospace;    
}

.userword{
    color: #12103c;
    font-weight: bold;
    font-family:monospace;    
    font-size: xxx-large;
}


.upword{
    color: #12103c;
    font-weight: bold;
    font-family:monospace;    
    font-size: xx-large;

}

.status{
    padding: 10px 10px;
    background-color: #232323; 
    color: #ffffff;
    font-size: medium;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.files_status{
    font-weight: bold;
    font-size: x-large;
    font-family:monospace;
}

.files_list_up{
    padding: 10px 10px;
    background-color: #ececec; 
    color: #080000;
    font-size: medium;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.files_list_down{
    padding: 10px 10px;
    background-color: #ececec; 
    color: #080000;
    font-size: x-large;
    font-weight: bold;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
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

.btn_archive{
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

.btn_back {
    padding: 2px 10px 2px;
    background-color: #a19636; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.admin_mid{
    color: #000000; 
    font-size: x-large;
    font-weight: bold;
    font-family:monospace;    
    animation-duration: 10s;
}
@keyframes fader_admin_failed {from {color: #ff0000;} to {color: #000000; } }
@keyframes fader_admin_success {from {color: #22ff00;} to {color: #000000; } }
"""
)
# ******************************************************************************************

















