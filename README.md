## ShareFly

Flask based web app for sharing files and quiz evaluation

## Quickstart

### Installation


1. Install the required dependencies

    ```bash
    python -m pip install Flask Flask-WTF waitress nbconvert 
    ```

    Note: the `nbconvert` package is optional - required only for the **Board** Page


2. Install `sharefly` using any **one** of the two options below:
    * Install from [PyPI](https://pypi.org/project/sharefly/)  

        ```bash
        python -m pip install sharefly
        ```
    * Install from [GitHub](https://github.com/NelsonSharma/sharefly) 

        ```bash
        git clone https://github.com/NelsonSharma/sharefly.git
        python -m pip install -e ./sharefly
        ```

### Hosting a Server

Start a server

```bash
python -m sharefly
```
Note: 
* The above command will start the server on all IP-Interfaces on port `8888` by default
* The server-side files will be stored in the current directory - this can be changed using `--dir` argument
* The config file `__config__.py` will be created in the current directory (if not existing)
* Access the app using a browser by going to `http://localhost:8888`
* The default uid or username is the username in the operating system
* The default password is not set - it must be set on the first login
* The default user has admin privileges
* To create more users and/or change access levels - edit the `__login__.csv` file found in the `__base__` directory


See more options to start a server using `--help` option

```bash
python -m sharefly --help
```


### Important

* **Memory Usage** :
    * ShareFly is a lightweight app that requires at least 60MB of RAM. Further memory usage depends on the number of registered users since the database of users is fully loaded and operated from RAM. It is meant for small scale environments such as private home, work and school networks. One should restrict having number of users to a maximum of 500 when using commodity hardware.
    * The offline database is stored in `csv` format and provides no security or ACID guarantees. The database is loaded when the server starts and is committed back to disk when the server stops. This means that if the app crashes, the changes in the database will not reflect. Admin users can manually persist the database to disk and reload it from the disk from the `/admin` page.

* **Sessions** :
    * It uses only `http` protocol and not `https`. Sessions are managed on server-side. The location of the file containing the `secret` for flask app can be specified in the `__configs__.py` script. If not specified i.e., left blank, it will auto generate a random secret. Generating a random secret every time means that the users will not remain logged in if the server is restarted.

