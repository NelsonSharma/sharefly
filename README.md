## ShareFly

Flask based web app for sharing files and quiz evaluation

## Quickstart

### Installation

Install the the `sharefly` module along with its requirements

```bash
python -m pip install Flask Flask-WTF waitress nbconvert sharefly
```

### Host Server

start a server 

```bash
python -m sharefly
```

see the options to start a server using `--help` option

```bash
python -m sharefly --help
```

```python
"""

options:
  -h, --help         show this help message and exit
  --dir DIR          path of workspace directory
  --verbose VERBOSE  verbose level in logging
  --log LOG          path of log dir - keep blank to disable logging
  --logpre LOGPRE    adds this to the start of logfile name (works when logging is enabled)
  --logname LOGNAME  name of logfile as formated string (works when logging is enabled)
  --logpost LOGPOST  adds this to the end of logfile name (works when logging is enabled)
  --con CON          config name - if not provided, uses 'default'
  --reg REG          if specified, allow users to register with specified access string such as DABU or DABUS+
  --cos COS          use 1 to create-on-start - create (overwrites) pages
  --coe COE          use 1 to clean-on-exit - deletes pages
  --access ACCESS    if specified, allow users to add access string such as DABU or DABUS+

"""
```

