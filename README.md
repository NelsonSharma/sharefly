## ShareFly

Flask based web app for sharing files and quiz evaluation

## Quickstart

### Installation

Install the the `sharefly` module along with its requirements

```bash
python -m pip install sharefly Flask Flask-WTF waitress nbconvert 
```

Note: the `nbconvert` package is optional - required only for the **Board** Page

### Host Server

Start a server (from current directory)

```bash
python -m sharefly
```
Note: The config file `config.py` can be found inside the current directory

See more options to start a server using `--help` option

```bash
python -m sharefly --help
```



